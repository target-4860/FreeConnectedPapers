<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">
        <h1>CONNECTED PAPERS</h1>
      </div>
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="handleSearch" 
          placeholder="输入论文关键词搜索..." 
          class="search-input"
        />
        <button @click="handleSearch" class="search-button">搜索</button>
      </div>
      <div class="nav-links">
        <a href="#" class="nav-link">分享</a>
        <a href="#" class="nav-link">关注</a>
        <a href="#" class="nav-link">关于</a>
        <a href="#" class="nav-link">价格</a>
        <a href="#" class="nav-link">登录</a>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="main-content">
      <!-- 左侧论文列表 -->
      <PaperList 
        :papers="papers" 
        :selectedPaper="selectedPaper" 
        @select-paper="selectPaper" 
        class="paper-list-container" 
      />

      <!-- 中间知识图谱 -->
      <KnowledgeGraph 
        :papers="papers"
        :selectedPaper="selectedPaper"
        @select-paper="selectPaper"
        class="knowledge-graph-container" 
      />

      <!-- 右侧问答区域 -->
      <QAPanel 
        :selectedPaper="selectedPaper" 
        class="qa-panel-container" 
      />
    </main>
  </div>
</template>

<script>
import PaperList from './components/PaperList.vue';
import KnowledgeGraph from './components/KnowledgeGraph.vue';
import QAPanel from './components/QAPanel.vue';

export default {
  name: 'App',
  components: {
    PaperList,
    KnowledgeGraph,
    QAPanel
  },
  data() {
    return {
      searchQuery: '',
      papers: [],
      selectedPaper: null,
      isLoading: false
    }
  },
  methods: {
    handleSearch() {
      if (!this.searchQuery.trim()) return;
      
      this.isLoading = true;
      // 模拟API调用
      setTimeout(() => {
        // 示例数据
        this.papers = this.generateSampleData();
        this.selectedPaper = this.papers[0]; // 默认选中第一篇
        this.isLoading = false;
      }, 1000);
    },
    
    selectPaper(paper) {
      this.selectedPaper = paper;
    },
    
    generateSampleData() {
      // 生成示例论文数据
      return [
        { 
          id: 1, 
          title: 'GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models',
          authors: ['Alex Nichol', '+ 6 authors', 'Mark Chen'],
          year: 2021,
          citations: 3507,
          citations_count: 3507,
          references: [2, 3, 5, 8],
          abstract: 'Diffusion models have recently been shown to generate high-quality synthetic images, especially when paired with a guidance technique to trade off diversity for fidelity.'
        },
        { 
          id: 2, 
          title: 'Hierarchical Text-Conditional Image Generation with CLIP Latents',
          authors: ['A. Ramesh', 'Prafulla Dhariwal', 'Alex Nichol', 'Casey Chu', 'Mark Chen'],
          year: 2022,
          citations_count: 2250,
          references: [1, 3, 4]
        },
        { 
          id: 3, 
          title: 'Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding',
          authors: ['Chitwan Saharia', 'William Chan', 'Saurabh Saxena', 'Lala Li', 'Jay Whang'],
          year: 2022,
          citations_count: 1820,
          references: [1, 2, 5]
        },
        { 
          id: 4, 
          title: 'High-Resolution Image Synthesis with Latent Diffusion Models',
          authors: ['Robin Rombach', 'A. Blattmann', 'Dominik Lorenz', 'Patrick Esser', 'B. Ommer'],
          year: 2021,
          citations_count: 1950,
          references: [1, 2, 3, 5]
        },
        { 
          id: 5, 
          title: 'Diffusion Models Beat GANs on Image Synthesis',
          authors: ['Prafulla Dhariwal', 'Alex Nichol'],
          year: 2021,
          citations_count: 1750,
          references: [2, 4, 8]
        },
        { 
          id: 6, 
          title: 'Zero-Shot Text-to-Image Generation',
          authors: ['A. Ramesh', 'Mikhail Pavlov', 'Gabriel Goh', 'Scott Gray'],
          year: 2021,
          citations_count: 1670,
          references: [1, 2, 3]
        },
        { 
          id: 7, 
          title: 'Classifier-Free Diffusion Guidance',
          authors: ['Jonathan Ho'],
          year: 2022,
          citations_count: 980,
          references: [1, 3, 5]
        },
        { 
          id: 8, 
          title: 'Denoising Diffusion Probabilistic Models',
          authors: ['Jonathan Ho', 'Ajay Jain', 'P. Abbeel'],
          year: 2020,
          citations_count: 2430,
          references: [5]
        }
      ];
    }
  },
  mounted() {
    // 页面加载时执行一次默认搜索
    this.searchQuery = 'Diffusion Models';
    this.handleSearch();
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  color: #333;
  background-color: #f5f5f5;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* 顶部导航栏样式 */
.header {
  display: flex;
  align-items: center;
  padding: 0.8rem 1.5rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo h1 {
  color: #2a7d8b;
  font-size: 1.2rem;
  font-weight: bold;
  margin-right: 1.5rem;
}

.search-container {
  display: flex;
  flex: 1;
  max-width: 500px;
  margin: 0 1rem;
}

.search-input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 0.9rem;
}

.search-button {
  padding: 0.5rem 1rem;
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 0.9rem;
}

.nav-links {
  display: flex;
  margin-left: auto;
}

.nav-link {
  margin-left: 1.5rem;
  color: #555;
  text-decoration: none;
  font-size: 0.9rem;
}

.nav-link:hover {
  color: #2a7d8b;
}

/* 主要内容区样式 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.paper-list-container {
  width: 25%;
  overflow-y: auto;
  border-right: 1px solid #eee;
  background-color: white;
}

.knowledge-graph-container {
  width: 50%;
  overflow: hidden;
  position: relative;
}

.qa-panel-container {
  width: 25%;
  overflow-y: auto;
  border-left: 1px solid #eee;
  background-color: white;
}
</style> 