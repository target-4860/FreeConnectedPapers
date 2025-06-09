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
    <main class="main-content">
      <!-- 左侧数据来源面板 -->
      <DataSourcePanel 
        :searchQuery="searchQuery" 
        :selectedItem="selectedItem" 
        @select-item="selectItem" 
        class="data-source-container" 
      />

      <!-- 中间知识图谱 -->
      <KnowledgeGraph 
        :papers="items"
        :selectedPaper="selectedItem"
        @search-term="handleGraphSearch"
        class="knowledge-graph-container" 
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
      showDetailModal: false
    }
  },
  methods: {
    handleSearch() {
      if (!this.searchQuery.trim()) return;
      
      this.isLoading = true;
      // 模拟API调用
      setTimeout(() => {
        // 示例数据
        this.items = this.generateSampleData();
        this.selectedItem = this.items[0]; // 默认选中第一篇
        this.isLoading = false;
      }, 1000);
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
    
    generateSampleData() {
      // 生成示例论文数据
      return [
        { 
          id: 1, 
          title: '高血压诊断与治疗指南',
          authors: ['中国高血压联盟', '中华医学会心血管病学分会'],
          year: 2022,
          citations_count: 3507,
          sourceType: 'guideline',
          references: [2, 3, 5, 8],
          keywords: ['高血压', '诊断', '治疗', '随访'],
          recommendations: [
            '建议所有成人定期测量血压',
            '对于一级高血压患者，建议首先进行生活方式干预'
          ]
        },
        { 
          id: 2, 
          title: '内科学（第9版）',
          authors: ['葛均波', '徐永健'],
          year: 2018,
          citations_count: 2250,
          sourceType: 'textbook',
          references: [1, 3, 4],
          publisher: '人民卫生出版社',
          keywords: ['高血压', '糖尿病', '心血管疾病'],
          sections: [
            {
              title: '第5章 高血压',
              content: `高血压是常见的慢性病，是心脑血管疾病的主要危险因素。随着人口老龄化，高血压的患病率逐年升高。高血压是以体循环动脉压增高为主要特征的临床综合征，可伴有心、脑、肾等器官的功能或器质性损害。`
            }
          ]
        },
        { 
          id: 3, 
          title: 'Hypertension Management in 2023: A Comprehensive Review',
          authors: ['Smith J', 'Johnson R', 'Williams T'],
          year: 2023,
          citations_count: 1820,
          sourceType: 'paper',
          references: [1, 2, 5],
          journal: 'Journal of Hypertension',
          keywords: ['高血压', '治疗', '管理'],
          abstract: '本文综述了高血压管理的最新进展，包括诊断标准、药物治疗和生活方式干预。'
        },
        { 
          id: 4, 
          title: '某三甲医院高血压患者电子病历分析',
          authors: ['张医生', '李医生'],
          year: 2022,
          citations_count: 1950,
          sourceType: 'emr',
          references: [1, 2, 3, 5],
          hospital: '北京协和医院',
          patientCount: 500,
          keywords: ['高血压', '并发症', '治疗效果'],
          summary: '本研究分析了500例高血压患者的电子病历数据，探讨了不同治疗方案的效果比较。'
        },
        { 
          id: 5, 
          title: '病理生理学（第3版）',
          authors: ['王建枝', '殷莲华'],
          year: 2020,
          citations_count: 1750,
          sourceType: 'textbook',
          references: [2, 4, 8],
          publisher: '高等教育出版社',
          keywords: ['高血压', '病理机制', '肾素-血管紧张素系统'],
          sections: [
            {
              title: '第7章 高血压的病理生理学',
              content: `高血压的发病机制复杂，包括肾素-血管紧张素-醛固酮系统激活、交感神经系统功能亢进、血管内皮功能障碍等多种因素。`
            }
          ]
        },
        { 
          id: 6, 
          title: '高血压与脑卒中相关性研究',
          authors: ['刘研究', '王学者'],
          year: 2021,
          citations_count: 1670,
          sourceType: 'paper',
          references: [1, 2, 3],
          journal: '中华医学杂志',
          keywords: ['高血压', '脑卒中', '风险因素'],
          abstract: '本研究探讨了高血压与脑卒中发生风险的相关性，分析了不同血压水平对脑卒中风险的影响。'
        },
        { 
          id: 7, 
          title: '高血压合并糖尿病患者临床特点分析',
          authors: ['赵医生'],
          year: 2022,
          citations_count: 980,
          sourceType: 'emr',
          references: [1, 3, 5],
          hospital: '上海第一人民医院',
          patientCount: 350,
          keywords: ['高血压', '糖尿病', '并发症'],
          summary: '本研究分析了350例高血压合并糖尿病患者的临床特点，探讨了两种疾病的相互影响及治疗策略。'
        },
        { 
          id: 8, 
          title: '中国高血压流行病学调查报告',
          authors: ['中国疾病预防控制中心', '国家心血管病中心'],
          year: 2020,
          citations_count: 2430,
          sourceType: 'guideline',
          references: [5],
          organization: '中国疾病预防控制中心',
          keywords: ['高血压', '流行病学', '患病率', '知晓率'],
          recommendations: [
            '加强高血压防治知识的宣传教育',
            '推广健康生活方式，减少高血压发病风险'
          ]
        }
      ];
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
}

.data-source-container {
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