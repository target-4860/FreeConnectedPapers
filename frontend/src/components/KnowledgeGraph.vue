<template>
  <div class="knowledge-graph-wrapper">
    <div class="knowledge-graph" v-if="isVisible">
      <div class="graph-controls">
        <button @click="resetGraph" class="control-button">
          重置视图
        </button>
        <button @click="centerGraph" class="control-button">
          居中
        </button>
      </div>
      
      <!-- 添加图例 -->
      <div class="graph-legend">
        <div class="legend-title">数据类型</div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #4CAF50;"></div>
          <div class="legend-label">教材</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #2196F3;"></div>
          <div class="legend-label">论文</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #FF9800;"></div>
          <div class="legend-label">电子病历</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #9C27B0;"></div>
          <div class="legend-label">临床指南</div>
        </div>
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
    },
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['search-term', 'update:isVisible'],
  data() {
    return {
      simulation: null,
      svg: null,
      width: 0,
      height: 0,
      nodes: [],
      links: [],
      isLoading: false,
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
    generateGraphData() {
      // 对数据进行抽样：如果超过50条数据，随机抽取50条
      let sampledPapers = [...this.papers];
      
      if (sampledPapers.length > 50) {
        console.log(`数据总量为 ${sampledPapers.length} 条，进行随机抽样选取50条`);
        sampledPapers = this.randomSample(sampledPapers, 50);
      } else {
        console.log(`数据总量为 ${sampledPapers.length} 条，使用全部数据`);
      }
      
      // 生成节点数据
      this.nodes = sampledPapers.map(paper => ({
        id: paper.id,
        title: paper.title,
        authors: paper.authors,
        year: paper.year,
        citations: paper.citations_count || 0,
        r: this.calculateRadius(paper.citations_count || 0),
        keywords: paper.keywords || [],
        sourceType: paper.sourceType // 添加数据源类型
      }));
      
      // 生成连接数据
      this.links = [];
      sampledPapers.forEach(paper => {
        if (paper.references && paper.references.length) {
          paper.references.forEach(refId => {
            // 检查引用的论文是否在我们的抽样数据集中
            const targetPaper = sampledPapers.find(p => p.id === refId);
            if (targetPaper) {
              this.links.push({
                source: paper.id,
                target: refId,
                value: 1
              });
            }
          });
        }
      });
      
      // 确保所有节点都连接起来，形成一个统一的网络
      
      // 第一步：基于关键词连接节点
      const nodesByKeyword = {};
      this.nodes.forEach(node => {
        if (node.keywords && node.keywords.length) {
          node.keywords.forEach(keyword => {
            if (!nodesByKeyword[keyword]) {
              nodesByKeyword[keyword] = [];
            }
            nodesByKeyword[keyword].push(node);
          });
        }
      });
      
      // 为共享同一关键词的节点创建连接
      Object.values(nodesByKeyword).forEach(keywordNodes => {
        if (keywordNodes.length > 1) {
          for (let i = 0; i < keywordNodes.length - 1; i++) {
            for (let j = i + 1; j < keywordNodes.length; j++) {
              // 检查是否已存在连接
              const exists = this.links.some(
                link => (link.source === keywordNodes[i].id && link.target === keywordNodes[j].id) ||
                        (link.source === keywordNodes[j].id && link.target === keywordNodes[i].id)
              );
              
              if (!exists) {
                this.links.push({
                  source: keywordNodes[i].id,
                  target: keywordNodes[j].id,
                  value: 0.7 // 中等强度的连接
                });
              }
            }
          }
        }
      });
      
      // 第二步：基于数据源类型连接节点
      const nodesByType = {};
      this.nodes.forEach(node => {
        if (!nodesByType[node.sourceType]) {
          nodesByType[node.sourceType] = [];
        }
        nodesByType[node.sourceType].push(node);
      });
      
      // 为每种类型内的节点创建连接
      Object.values(nodesByType).forEach(typeNodes => {
        if (typeNodes.length > 1) {
          // 创建类型内部连接 - 环形结构
          for (let i = 0; i < typeNodes.length; i++) {
            const nextIndex = (i + 1) % typeNodes.length; // 循环连接
            
            // 检查是否已存在连接
            const exists = this.links.some(
              link => (link.source === typeNodes[i].id && link.target === typeNodes[nextIndex].id) ||
                      (link.source === typeNodes[nextIndex].id && link.target === typeNodes[i].id)
            );
            
            if (!exists) {
              this.links.push({
                source: typeNodes[i].id,
                target: typeNodes[nextIndex].id,
                value: 0.5 // 较弱的连接
              });
            }
          }
        }
      });
      
      // 第三步：检查是否有孤立的节点组，如果有，则将它们连接到主网络
      const connectedGroups = this.findConnectedGroups();
      
      if (connectedGroups.length > 1) {
        // 按组大小排序（从大到小）
        connectedGroups.sort((a, b) => b.length - a.length);
        
        // 最大的组被视为主网络
        const mainGroup = connectedGroups[0];
        
        // 将其他组连接到主网络
        for (let i = 1; i < connectedGroups.length; i++) {
          const group = connectedGroups[i];
          
          // 从每个组中选择一个节点连接到主网络
          const sourceNode = group[0];
          const targetNode = mainGroup[0];
          
          this.links.push({
            source: sourceNode,
            target: targetNode,
            value: 0.3 // 弱连接
          });
        }
      }
      
      console.log(`生成了 ${this.nodes.length} 个节点和 ${this.links.length} 条连接，连接组数: ${this.findConnectedGroups().length}`);
    },
    
    calculateRadius(citations) {
      // 根据引用数量计算节点大小
      return Math.max(Math.min(Math.log(citations + 1) * 4 + 10, 25), 10);
    },
    
    getNodeColor(sourceType, year) {
      // 根据数据源类型和年份分配颜色
      const currentYear = new Date().getFullYear();
      const yearsAgo = currentYear - year;
      
      // 为不同数据源类型定义基础颜色
      let baseColor;
      switch(sourceType) {
        case 'textbook':
          baseColor = "#4CAF50"; // 教材 - 绿色
          break;
        case 'paper':
          baseColor = "#2196F3"; // 论文 - 蓝色
          break;
        case 'emr':
          baseColor = "#FF9800"; // 电子病历 - 橙色
          break;
        case 'guideline':
          baseColor = "#9C27B0"; // 临床指南 - 紫色
          break;
        default:
          baseColor = "#607D8B"; // 默认 - 灰色
      }
      
      // 根据年份调整颜色深浅
      if (yearsAgo <= 1) return this.adjustColorBrightness(baseColor, 40); // 最新 - 最亮
      if (yearsAgo <= 3) return this.adjustColorBrightness(baseColor, 20);
      if (yearsAgo <= 5) return baseColor; // 原始颜色
      if (yearsAgo <= 10) return this.adjustColorBrightness(baseColor, -20);
      return this.adjustColorBrightness(baseColor, -40); // 最旧 - 最暗
    },
    
    // 辅助函数：调整颜色亮度
    adjustColorBrightness(hex, percent) {
      // 将十六进制颜色转换为RGB
      let r = parseInt(hex.substring(1, 3), 16);
      let g = parseInt(hex.substring(3, 5), 16);
      let b = parseInt(hex.substring(5, 7), 16);
      
      // 应用亮度调整
      r = Math.max(0, Math.min(255, r + percent));
      g = Math.max(0, Math.min(255, g + percent));
      b = Math.max(0, Math.min(255, b + percent));
      
      // 转回十六进制格式
      return "#" + 
        ((1 << 24) + (r << 16) + (g << 8) + b)
          .toString(16)
          .slice(1);
    },
    
    getSourceTypeName(sourceType) {
      // 获取数据源类型的中文名称
      const sourceTypes = {
        'textbook': '教材',
        'paper': '论文',
        'emr': '电子病历',
        'guideline': '临床指南'
      };
      return sourceTypes[sourceType] || sourceType;
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
        .force("link", d3.forceLink(this.links).id(d => d.id).distance(150))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(this.width / 2, this.height / 2))
        .force("collide", d3.forceCollide().radius(d => d.r + 20));
      
      // 绘制连接线
      const link = g.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(this.links)
        .join("line")
        .attr("stroke-width", d => Math.sqrt(d.value) * 1.5);
      
      // 绘制节点
      const node = g.append("g")
        .selectAll(".node")
        .data(this.nodes)
        .join("g")
        .attr("class", "node")
        .call(this.drag(this.simulation));
      
      // 使用纯色圆形节点，根据数据源类型设置不同颜色
      node.append("circle")
        .attr("r", d => d.r)
        .attr("fill", d => this.getNodeColor(d.sourceType, d.year))
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
        .text(d => `${d.title}\n类型: ${this.getSourceTypeName(d.sourceType)}\n作者: ${d.authors ? d.authors.join(", ") : "未知"}\n年份: ${d.year || "未知"}\n引用数: ${d.citations || 0}\n点击可搜索相关内容`);
      
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
    },
    
    // 辅助方法：查找连接的节点组
    findConnectedGroups() {
      const nodeIds = this.nodes.map(n => n.id);
      const visited = {};
      const groups = [];
      
      // 深度优先搜索找出连接的组件
      const dfs = (nodeId, group) => {
        visited[nodeId] = true;
        group.push(nodeId);
        
        // 查找所有与该节点相连的节点
        this.links.forEach(link => {
          const nextId = link.source === nodeId ? link.target : 
                         link.target === nodeId ? link.source : null;
          
          if (nextId !== null && !visited[nextId]) {
            dfs(nextId, group);
          }
        });
      };
      
      // 对每个未访问的节点进行DFS
      nodeIds.forEach(id => {
        if (!visited[id]) {
          const group = [];
          dfs(id, group);
          groups.push(group);
        }
      });
      
      return groups;
    },
    
    // 随机抽样方法
    randomSample(array, sampleSize) {
      // Fisher-Yates 洗牌算法
      const shuffled = [...array];
      let i = array.length;
      while (i--) {
        const index = Math.floor(Math.random() * (i + 1));
        [shuffled[index], shuffled[i]] = [shuffled[i], shuffled[index]];
      }
      
      // 智能抽样：保证各类型数据都有代表
      const byType = {};
      shuffled.forEach(item => {
        if (!byType[item.sourceType]) {
          byType[item.sourceType] = [];
        }
        byType[item.sourceType].push(item);
      });
      
      // 结果数组
      const result = [];
      
      // 确保每种类型至少有一个代表
      Object.values(byType).forEach(items => {
        if (items.length > 0) {
          result.push(items[0]);
        }
      });
      
      // 计算各类型在原始数据中的比例
      const typeProportions = {};
      let totalItems = 0;
      Object.entries(byType).forEach(([type, items]) => {
        totalItems += items.length;
        typeProportions[type] = items.length;
      });
      
      // 按比例分配剩余配额
      if (result.length < sampleSize) {
        const remaining = sampleSize - result.length;
        let allocated = 0;
        Object.entries(typeProportions).forEach(([type, count], index) => {
          // 最后一种类型分配所有剩余配额
          if (index === Object.keys(typeProportions).length - 1) {
            const toAllocate = remaining - allocated;
            if (toAllocate > 0 && byType[type].length > 1) {
              result.push(...byType[type].slice(1, 1 + toAllocate));
            }
          } else {
            const proportion = count / totalItems;
            const toAllocate = Math.min(
              Math.max(1, Math.floor(proportion * remaining)),
              byType[type].length - 1
            );
            
            if (toAllocate > 0) {
              result.push(...byType[type].slice(1, 1 + toAllocate));
              allocated += toAllocate;
            }
          }
        });
      }
      
      // 如果配额分配后还不足，用随机数据补足
      if (result.length < sampleSize) {
        const usedIds = new Set(result.map(item => item.id));
        const remainingItems = shuffled.filter(item => !usedIds.has(item.id));
        const neededCount = sampleSize - result.length;
        
        if (remainingItems.length > 0) {
          result.push(...remainingItems.slice(0, neededCount));
        }
      }
      
      console.log(`抽样分布: ${Object.entries(byType).map(([type, items]) => 
        `${type}: ${result.filter(item => item.sourceType === type).length}/${items.length}`
      ).join(', ')}`);
      
      return result;
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
  transition: all 0.3s ease;
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

.graph-legend {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.7rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.legend-title {
  font-weight: 500;
  margin-bottom: 0.7rem;
  font-size: 0.9rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3rem;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  margin-right: 0.8rem;
}

.legend-label {
  font-size: 0.85rem;
  color: #333;
}
</style> 