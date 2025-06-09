<template>
  <div class="knowledge-graph-wrapper">
    <!-- 知识图谱按钮 -->
    <div class="graph-toggle-container">
      <button @click="toggleGraphVisibility" class="toggle-button">
        {{ isVisible ? '隐藏知识图谱' : '显示知识图谱' }}
      </button>
    </div>
    
    <div class="knowledge-graph" v-if="isVisible">
      <div class="graph-controls">
        <button @click="resetGraph" class="control-button">
          重置视图
        </button>
        <button @click="centerGraph" class="control-button">
          居中
        </button>
      </div>
      
      <div class="loading-overlay" v-if="isLoading">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>
      
      <div ref="graphContainer" class="graph-container"></div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'KnowledgeGraph',
  props: {
    papers: {
      type: Array,
      default: () => []
    },
    selectedPaper: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      simulation: null,
      svg: null,
      width: 0,
      height: 0,
      nodes: [],
      links: [],
      isLoading: false,
      isVisible: false, // 默认隐藏知识图谱
      transform: {
        x: 0,
        y: 0,
        k: 1
      }
    }
  },
  watch: {
    papers: {
      handler(newPapers) {
        if (newPapers.length > 0 && this.isVisible) {
          this.isLoading = true;
          setTimeout(() => {
            this.generateGraphData();
            this.initializeGraph();
            this.isLoading = false;
          }, 500);
        }
      },
      deep: true
    },
    selectedPaper(newPaper) {
      if (newPaper && this.svg && this.isVisible) {
        this.highlightNode(newPaper.id);
      }
    },
    isVisible(newValue) {
      if (newValue && this.papers.length > 0) {
        // 当图谱变为可见时，初始化图谱
        this.$nextTick(() => {
          this.isLoading = true;
          setTimeout(() => {
            this.generateGraphData();
            this.initializeGraph();
            this.isLoading = false;
          }, 500);
        });
      }
    }
  },
  methods: {
    toggleGraphVisibility() {
      this.isVisible = !this.isVisible;
    },
    
    generateGraphData() {
      // 生成节点数据
      this.nodes = this.papers.map(paper => ({
        id: paper.id,
        title: paper.title,
        authors: paper.authors,
        year: paper.year,
        citations: paper.citations_count || 0,
        r: this.calculateRadius(paper.citations_count || 0),
        keywords: paper.keywords || []
      }));
      
      // 生成连接数据
      this.links = [];
      this.papers.forEach(paper => {
        if (paper.references && paper.references.length) {
          paper.references.forEach(refId => {
            // 检查引用的论文是否在我们的数据集中
            if (this.papers.some(p => p.id === refId)) {
              this.links.push({
                source: paper.id,
                target: refId,
                value: 1
              });
            }
          });
        }
      });
    },
    
    calculateRadius(citations) {
      // 根据引用数量计算节点大小
      return Math.max(Math.min(Math.log(citations + 1) * 4 + 10, 25), 10);
    },
    
    getNodeColor(year) {
      // 根据年份分配颜色
      const currentYear = new Date().getFullYear();
      const yearsAgo = currentYear - year;
      
      // 颜色范围从浅色（新）到深色（旧）
      if (yearsAgo <= 1) return "#60b3c2"; // 最新
      if (yearsAgo <= 3) return "#3c8b9c";
      if (yearsAgo <= 5) return "#2a7d8b";
      if (yearsAgo <= 10) return "#1a6575";
      return "#0d4e5d"; // 最旧
    },
    
    initializeGraph() {
      const container = this.$refs.graphContainer;
      if (!container) return;
      
      // 清除之前的图形
      d3.select(container).selectAll("*").remove();
      
      // 获取容器尺寸
      this.width = container.clientWidth;
      this.height = container.clientHeight;
      
      // 创建SVG
      this.svg = d3.select(container)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", [0, 0, this.width, this.height]);
      
      // 添加缩放和平移功能
      const zoom = d3.zoom()
        .scaleExtent([0.2, 3])
        .on("zoom", (event) => {
          this.transform = event.transform;
          g.attr("transform", event.transform);
        });
      
      this.svg.call(zoom);
      
      const g = this.svg.append("g");
      
      // 创建力导向图
      this.simulation = d3.forceSimulation(this.nodes)
        .force("link", d3.forceLink(this.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(this.width / 2, this.height / 2))
        .force("collide", d3.forceCollide().radius(d => d.r + 10));
      
      // 绘制连接线
      const link = g.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(this.links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.value));
      
      // 绘制节点
      const node = g.append("g")
        .selectAll(".node")
        .data(this.nodes)
        .join("g")
        .attr("class", "node")
        .call(this.drag(this.simulation));
      
      // 节点圆形
      node.append("circle")
        .attr("r", d => d.r)
        .attr("fill", d => this.getNodeColor(d.year))
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .on("click", (event, d) => {
          // 点击节点时触发重新搜索
          this.searchNodeKeywords(d);
        });
      
      // 节点文本
      node.append("text")
        .text(d => this.getTruncatedTitle(d.title))
        .attr("dy", d => d.r + 15)
        .attr("text-anchor", "middle")
        .attr("font-size", "8px")
        .attr("fill", "#333");
      
      // 添加悬停提示
      node.append("title")
        .text(d => `${d.title}\n作者: ${d.authors ? d.authors.join(", ") : "未知"}\n年份: ${d.year || "未知"}\n引用数: ${d.citations || 0}\n点击可搜索相关内容`);
      
      // 更新力导向图
      this.simulation.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
        
        node.attr("transform", d => `translate(${d.x},${d.y})`);
      });
    },
    
    drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    },
    
    getTruncatedTitle(title) {
      if (!title) return '';
      return title.length > 20 ? title.substring(0, 20) + '...' : title;
    },
    
    highlightNode(nodeId) {
      if (!this.svg) return;
      
      // 重置所有节点
      this.svg.selectAll("circle")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5);
      
      // 高亮选中的节点
      this.svg.selectAll(".node").each(function(d) {
        if (d.id === nodeId) {
          d3.select(this).select("circle")
            .attr("stroke", "#ff5722")
            .attr("stroke-width", 3);
        }
      });
    },
    
    resetGraph() {
      if (!this.svg) return;
      
      const container = this.$refs.graphContainer;
      const width = container.clientWidth;
      const height = container.clientHeight;
      
      // 重置缩放和平移
      this.svg.transition()
        .duration(750)
        .call(
          d3.zoom().transform,
          d3.zoomIdentity.translate(0, 0).scale(1)
        );
      
      // 重新开始模拟
      this.simulation
        .alpha(0.3)
        .restart();
    },
    
    centerGraph() {
      if (!this.svg || !this.selectedPaper) return;
      
      const container = this.$refs.graphContainer;
      const width = container.clientWidth;
      const height = container.clientHeight;
      
      // 查找选中节点
      const selectedNode = this.nodes.find(n => n.id === this.selectedPaper.id);
      
      if (selectedNode) {
        // 计算居中变换
        const scale = 1.5;
        const x = width / 2 - selectedNode.x * scale;
        const y = height / 2 - selectedNode.y * scale;
        
        // 应用变换
        this.svg.transition()
          .duration(750)
          .call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(x, y).scale(scale)
          );
        
        // 高亮节点
        this.highlightNode(selectedNode.id);
      }
    },
    
    searchNodeKeywords(node) {
      // 提取节点关键词或标题作为搜索词
      let searchTerm = '';
      
      if (node.keywords && node.keywords.length > 0) {
        // 使用第一个关键词作为搜索词
        searchTerm = node.keywords[0];
      } else {
        // 如果没有关键词，使用标题中的前几个词
        const titleWords = node.title.split(' ');
        searchTerm = titleWords.length > 3 ? titleWords.slice(0, 3).join(' ') : node.title;
      }
      
      // 触发搜索事件
      this.$emit('search-term', searchTerm);
    }
  },
  mounted() {
    // 窗口大小变化时重新渲染图谱
    window.addEventListener('resize', () => {
      if (this.isVisible) {
        this.initializeGraph();
      }
    });
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.initializeGraph);
    if (this.simulation) {
      this.simulation.stop();
    }
  }
}
</script>

<style scoped>
.knowledge-graph-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.graph-toggle-container {
  padding: 1rem;
  display: flex;
  justify-content: center;
  background-color: #f9fafb;
  border-bottom: 1px solid #eee;
}

.toggle-button {
  padding: 0.6rem 1.2rem;
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-button:hover {
  background-color: #1a6575;
}

.knowledge-graph {
  position: relative;
  flex: 1;
  width: 100%;
  background-color: #f9fafb;
  overflow: hidden;
}

.graph-container {
  width: 100%;
  height: 100%;
}

.graph-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
  display: flex;
  gap: 0.5rem;
}

.control-button {
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.control-button:hover {
  background-color: #2a7d8b;
  color: white;
  border-color: #2a7d8b;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 20;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(42, 125, 139, 0.2);
  border-radius: 50%;
  border-top-color: #2a7d8b;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 1rem;
  color: #2a7d8b;
  font-weight: 500;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 