<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">
        <h1>医学知识图谱系统</h1>
      </div>
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="handleSearch" 
          placeholder="输入医学关键词搜索..." 
          class="search-input"
        />
        <button @click="handleSearch" class="search-button">搜索</button>
      </div>
      <div class="nav-links">
        <a href="#" class="nav-link">分享</a>
        <a href="#" class="nav-link">关注</a>
        <a href="#" class="nav-link">关于</a>
        <a href="#" class="nav-link">登录</a>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="main-content" :class="{'graph-hidden': !graphVisible}">
      <!-- 左侧数据来源面板 -->
      <DataSourcePanel 
        :searchQuery="searchQuery" 
        :selectedItem="selectedItem" 
        @select-item="selectItem" 
        :class="['data-source-container', {'expanded': !graphVisible}]" 
        :isExpanded="!graphVisible"
      />

      <!-- 知识图谱显示/隐藏按钮 -->
      <div class="graph-toggle-btn">
        <button @click="toggleGraphVisibility" class="toggle-button">
          {{ graphVisible ? '隐藏知识图谱' : '显示知识图谱' }}
        </button>
      </div>

      <!-- 中间知识图谱 -->
      <KnowledgeGraph 
        :papers="items"
        :selectedPaper="selectedItem"
        @search-term="handleGraphSearch"
        class="knowledge-graph-container"
        v-model:isVisible="graphVisible"
      />

      <!-- 右侧问答区域 -->
      <QAPanel 
        :selectedItem="selectedItem" 
        :searchQuery="searchQuery"
        class="qa-panel-container" 
      />
    </main>
    
    <!-- 详细信息弹窗 -->
    <DetailModal
      :show="showDetailModal"
      :item="selectedItem"
      :searchQuery="searchQuery"
      @close="closeDetailModal"
      @search-keyword="handleKeywordSearch"
    />
  </div>
</template>

<script>
import DataSourcePanel from './components/PaperList.vue';
import KnowledgeGraph from './components/KnowledgeGraph.vue';
import QAPanel from './components/QAPanel.vue';
import DetailModal from './components/DetailModal.vue';

export default {
  name: 'App',
  components: {
    DataSourcePanel,
    KnowledgeGraph,
    QAPanel,
    DetailModal
  },
  data() {
    return {
      searchQuery: '',
      items: [],
      selectedItem: null,
      isLoading: false,
      showDetailModal: false,
      graphVisible: false // 控制知识图谱是否可见
    }
  },
  methods: {
    handleSearch() {
      if (!this.searchQuery.trim()) return;
      
      this.isLoading = true;
      
      // 从数据服务加载实际数据，替换模拟数据
      import('./services/DataService').then(({ loadAllData, searchData }) => {
        loadAllData().then(allData => {
          // 使用搜索词过滤数据
          this.items = searchData(allData, this.searchQuery);
          if (this.items.length > 0) {
            this.selectedItem = this.items[0]; // 默认选中第一篇
          }
          this.isLoading = false;
          
          // 如果查询结果不为空且图谱不可见，则显示图谱
          if (this.items.length > 0 && !this.graphVisible) {
            this.graphVisible = true;
          }
        }).catch(error => {
          console.error('加载数据失败:', error);
          this.isLoading = false;
        });
      });
    },
    
    selectItem(item) {
      this.selectedItem = item;
      this.showDetailModal = true;
    },
    
    closeDetailModal() {
      this.showDetailModal = false;
    },
    
    handleGraphSearch(searchTerm) {
      this.searchQuery = searchTerm;
      this.handleSearch();
    },
    
    handleKeywordSearch(keyword) {
      this.searchQuery = keyword;
      this.handleSearch();
      this.showDetailModal = false; // 关闭详情弹窗
    },
    
    toggleGraphVisibility() {
      this.graphVisible = !this.graphVisible;
    }
  },
  mounted() {
    // 页面加载时执行一次默认搜索
    this.searchQuery = '高血压';
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
  position: relative; /* 添加相对定位，用于绝对定位切换按钮 */
}

.data-source-container {
  width: 25%;
  overflow-y: auto;
  border-right: 1px solid #eee;
  background-color: white;
  transition: width 0.3s ease;
}

.data-source-container.expanded {
  width: 75%; /* 当知识图谱隐藏时，数据源面板扩展到75% */
}

.knowledge-graph-container {
  width: 50%;
  overflow: hidden;
  position: relative;
  transition: width 0.3s ease;
}

/* 当知识图谱隐藏时，宽度变为0 */
.main-content.graph-hidden .knowledge-graph-container {
  width: 0;
  padding: 0;
  margin: 0;
  border: none;
}

.qa-panel-container {
  width: 25%;
  overflow-y: auto;
  border-left: 1px solid #eee;
  background-color: white;
}

/* 知识图谱显示/隐藏按钮样式 */
.graph-toggle-btn {
  position: absolute;
  top: 20px; /* 调整位置，与数据来源标题对齐 */
  left: 50%; /* 放在左侧数据面板右侧 */
  z-index: 100;
  padding: 0.5rem;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-button:hover {
  background-color: #1a6575;
}
</style> 