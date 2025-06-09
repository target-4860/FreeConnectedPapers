<template>
  <div class="data-source-panel">
    <div class="panel-header">
      <h2>数据来源</h2>
    </div>
    
    <div class="source-tabs">
      <div 
        v-for="(source, index) in dataSources" 
        :key="index"
        :class="['source-tab', { active: activeSource === source.type }]"
        @click="setActiveSource(source.type)"
      >
        {{ source.name }} <span class="count">({{ source.count }})</span>
      </div>
    </div>
    
    <div class="source-content">
      <template v-if="filteredItems.length > 0">
        <div 
          v-for="item in filteredItems" 
          :key="item.id" 
          class="source-item" 
          :class="{ 'selected': selectedItem && selectedItem.id === item.id }"
          @click="selectItem(item)"
        >
          <div class="item-title">{{ item.title }}</div>
          <div class="item-meta">
            <span class="item-source-type">{{ getSourceTypeName(item.sourceType) }}</span>
            <span class="item-year" v-if="item.year">{{ item.year }}</span>
          </div>
          <div class="item-authors" v-if="item.authors">{{ formatAuthors(item.authors) }}</div>
        </div>
      </template>
      
      <div v-else class="no-items">
        没有找到相关{{ getSourceTypeName(activeSource) }}，请尝试其他关键词
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataSourcePanel',
  props: {
    searchQuery: {
      type: String,
      default: ''
    },
    selectedItem: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      activeSource: 'all', // all, textbook, paper, emr, guideline
      dataSources: [
        { type: 'all', name: '全部', count: 0 },
        { type: 'textbook', name: '教材', count: 0 },
        { type: 'paper', name: '论文', count: 0 },
        { type: 'emr', name: '电子病历', count: 0 },
        { type: 'guideline', name: '临床指南', count: 0 }
      ],
      items: []
    }
  },
  computed: {
    filteredItems() {
      if (this.activeSource === 'all') {
        return this.items;
      }
      return this.items.filter(item => item.sourceType === this.activeSource);
    }
  },
  methods: {
    setActiveSource(sourceType) {
      this.activeSource = sourceType;
    },
    
    selectItem(item) {
      this.$emit('select-item', item);
    },
    
    formatAuthors(authors) {
      if (!authors || authors.length === 0) return '';
      if (authors.length === 1) return authors[0];
      return authors.slice(0, 2).join(', ') + (authors.length > 2 ? ' 等' : '');
    },
    
    getSourceTypeName(type) {
      const source = this.dataSources.find(s => s.type === type);
      return source ? source.name : '';
    },
    
    updateSourceCounts() {
      // 更新各数据源的数量
      this.dataSources.forEach(source => {
        if (source.type === 'all') {
          source.count = this.items.length;
        } else {
          source.count = this.items.filter(item => item.sourceType === source.type).length;
        }
      });
    },
    
    loadItems(query) {
      // 这里应该调用API获取搜索结果
      // 模拟API调用
      this.isLoading = true;
      
      setTimeout(() => {
        // 示例数据
        this.items = this.generateSampleData(query);
        this.updateSourceCounts();
        this.isLoading = false;
        
        // 如果有结果，默认选中第一个
        if (this.items.length > 0) {
          this.$emit('select-item', this.items[0]);
        }
      }, 500);
    },
    
    generateSampleData(query) {
      // 生成示例数据
      const sampleData = [
        {
          id: 1,
          title: '内科学（第9版）',
          sourceType: 'textbook',
          authors: ['葛均波', '徐永健'],
          year: 2018,
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
          id: 2,
          title: 'Hypertension Management in 2023: A Comprehensive Review',
          sourceType: 'paper',
          authors: ['Smith J', 'Johnson R', 'Williams T'],
          year: 2023,
          journal: 'Journal of Hypertension',
          keywords: ['高血压', '治疗', '管理'],
          abstract: '本文综述了高血压管理的最新进展，包括诊断标准、药物治疗和生活方式干预。'
        },
        {
          id: 3,
          title: '某三甲医院高血压患者电子病历分析',
          sourceType: 'emr',
          year: 2022,
          hospital: '北京协和医院',
          patientCount: 500,
          keywords: ['高血压', '并发症', '治疗效果'],
          summary: '本研究分析了500例高血压患者的电子病历数据，探讨了不同治疗方案的效果比较。'
        },
        {
          id: 4,
          title: '中国高血压防治指南（2023年修订版）',
          sourceType: 'guideline',
          authors: ['中国高血压联盟', '中华医学会心血管病学分会'],
          year: 2023,
          organization: '中国高血压联盟',
          keywords: ['高血压', '诊断', '治疗', '随访'],
          recommendations: [
            '建议所有成人定期测量血压',
            '对于一级高血压患者，建议首先进行生活方式干预'
          ]
        },
        {
          id: 5,
          title: '病理生理学（第3版）',
          sourceType: 'textbook',
          authors: ['王建枝', '殷莲华'],
          year: 2020,
          publisher: '高等教育出版社',
          keywords: ['高血压', '病理机制', '肾素-血管紧张素系统'],
          sections: [
            {
              title: '第7章 高血压的病理生理学',
              content: `高血压的发病机制复杂，包括肾素-血管紧张素-醛固酮系统激活、交感神经系统功能亢进、血管内皮功能障碍等多种因素。`
            }
          ]
        }
      ];
      
      // 根据查询词过滤
      if (query) {
        const lowerQuery = query.toLowerCase();
        return sampleData.filter(item => 
          item.title.toLowerCase().includes(lowerQuery) || 
          (item.keywords && item.keywords.some(k => k.toLowerCase().includes(lowerQuery)))
        );
      }
      
      return sampleData;
    }
  },
  watch: {
    searchQuery: {
      handler(newQuery) {
        if (newQuery) {
          this.loadItems(newQuery);
        }
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
.data-source-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fafafa;
}

.panel-header {
  padding: 1rem;
  background-color: #f0f0f0;
  border-bottom: 1px solid #e0e0e0;
}

.panel-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #444;
  margin: 0;
}

.source-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.source-tab {
  padding: 0.8rem 1rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.source-tab:hover {
  color: #2a7d8b;
  background-color: #f0f7f9;
}

.source-tab.active {
  color: #2a7d8b;
  border-bottom-color: #2a7d8b;
  background-color: #e6f3f7;
  font-weight: 500;
}

.count {
  font-size: 0.8rem;
  color: #888;
}

.source-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.source-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.source-item:hover {
  background-color: #f0f7f9;
}

.source-item.selected {
  background-color: #e6f3f7;
  border-left: 4px solid #2a7d8b;
}

.item-title {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  margin-bottom: 0.4rem;
}

.item-source-type {
  color: #2a7d8b;
  font-weight: 500;
  background-color: #e6f3f7;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.item-year {
  color: #888;
}

.item-authors {
  font-size: 0.85rem;
  color: #666;
}

.no-items {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-style: italic;
}
</style> 