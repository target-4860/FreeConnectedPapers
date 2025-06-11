<template>
  <div class="data-source-panel" :class="{'expanded': isExpanded}">
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
          
          <!-- 扩展模式下显示的额外信息 -->
          <div v-if="isExpanded" class="item-details">
            <!-- 关键词 -->
            <div v-if="item.keywords && item.keywords.length" class="item-keywords">
              <strong>关键词:</strong>
              <span 
                v-for="(keyword, idx) in item.keywords" 
                :key="idx" 
                class="keyword-tag"
                :class="{ 'highlight': isSearchKeyword(keyword) }"
              >
                {{ keyword }}
              </span>
            </div>
            
            <!-- 摘要/简介 -->
            <div v-if="item.abstract || item.summary" class="item-abstract">
              <strong>摘要:</strong>
              <p v-html="highlightText(item.abstract || item.summary)"></p>
            </div>
            
            <!-- 教材章节预览 -->
            <div v-if="item.sections && item.sections.length" class="item-section-preview">
              <strong>相关章节:</strong>
              <p>{{ item.sections[0].title }}</p>
            </div>
            
            <!-- 临床指南建议预览 -->
            <div v-if="item.recommendations && item.recommendations.length" class="item-recommendations">
              <strong>主要建议:</strong>
              <p v-html="highlightText(item.recommendations[0])"></p>
              <span v-if="item.recommendations.length > 1" class="more-link">更多建议...</span>
            </div>
            
            <!-- 其他元数据 -->
            <div class="item-metadata">
              <span v-if="item.publisher"><strong>出版社:</strong> {{ item.publisher }}</span>
              <span v-if="item.journal"><strong>期刊:</strong> {{ item.journal }}</span>
              <span v-if="item.hospital"><strong>医院:</strong> {{ item.hospital }}</span>
              <span v-if="item.organization"><strong>组织:</strong> {{ item.organization }}</span>
              <span v-if="item.citations_count"><strong>引用数:</strong> {{ item.citations_count }}</span>
            </div>
            
            <div class="view-details-button">
              <button @click.stop="viewFullDetails(item)">查看完整详情</button>
            </div>
          </div>
        </div>
      </template>
      
      <div v-else class="no-items">
        没有找到相关{{ getSourceTypeName(activeSource) }}，请尝试其他关键词
      </div>
    </div>
  </div>
</template>

<script>
import { loadAllData, searchData } from '../services/DataService';

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
    },
    isExpanded: {
      type: Boolean,
      default: false
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
      items: [],
      allItems: [], // 存储所有加载的数据
      isLoading: false
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
    
    viewFullDetails(item) {
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
    
    isSearchKeyword(keyword) {
      if (!this.searchQuery) return false;
      return keyword.toLowerCase().includes(this.searchQuery.toLowerCase());
    },
    
    highlightText(text) {
      if (!text || !this.searchQuery) return text;
      
      const regex = new RegExp(`(${this.searchQuery})`, 'gi');
      return text.replace(regex, '<span class="highlight-text">$1</span>');
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
    
    async loadAllDataFromServer() {
      this.isLoading = true;
      try {
        // 加载所有数据
        this.allItems = await loadAllData();
        console.log('加载了 ' + this.allItems.length + ' 条数据');
        
        // 如果有搜索查询，则过滤数据
        if (this.searchQuery) {
          this.items = searchData(this.allItems, this.searchQuery);
        } else {
          this.items = this.allItems;
        }
        
        this.updateSourceCounts();
        
        // 如果有结果，默认选中第一个 - 注释掉自动选择
        /*if (this.items.length > 0) {
          this.$emit('select-item', this.items[0]);
        }*/
      } catch (error) {
        console.error('加载数据失败:', error);
        this.items = [];
      } finally {
        this.isLoading = false;
      }
    },
    
    loadItems(query) {
      this.isLoading = true;
      
      // 如果已经加载了所有数据，则直接从内存中过滤
      if (this.allItems.length > 0) {
        this.items = searchData(this.allItems, query);
        this.updateSourceCounts();
        this.isLoading = false;
        
        // 如果有结果，默认选中第一个 - 注释掉自动选择
        /*if (this.items.length > 0) {
          this.$emit('select-item', this.items[0]);
        }*/
      } else {
        // 否则先加载所有数据
        this.loadAllDataFromServer();
      }
    }
  },
  mounted() {
    // 组件挂载时加载所有数据
    this.loadAllDataFromServer();
  },
  watch: {
    searchQuery: {
      handler(newQuery) {
        this.loadItems(newQuery);
      }
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

.data-source-panel.expanded .source-item {
  padding: 1.5rem;
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
  flex-wrap: wrap;
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

/* 扩展模式下的额外样式 */
.item-details {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #ddd;
}

.item-keywords {
  margin-bottom: 0.8rem;
}

.keyword-tag {
  display: inline-block;
  margin: 0.2rem;
  padding: 0.2rem 0.5rem;
  background-color: #f0f0f0;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #555;
}

.keyword-tag.highlight {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: 500;
}

.item-abstract, .item-section-preview, .item-recommendations {
  margin-bottom: 0.8rem;
  font-size: 0.9rem;
  line-height: 1.5;
}

.item-abstract p, .item-section-preview p, .item-recommendations p {
  margin-top: 0.3rem;
  color: #555;
}

.item-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-bottom: 0.8rem;
  font-size: 0.85rem;
  color: #666;
}

.more-link {
  color: #2a7d8b;
  font-size: 0.8rem;
  cursor: pointer;
  display: block;
  margin-top: 0.3rem;
}

.view-details-button {
  margin-top: 1rem;
  text-align: right;
}

.view-details-button button {
  padding: 0.4rem 0.8rem;
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.view-details-button button:hover {
  background-color: #1a6575;
}

:deep(.highlight-text) {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}
</style> 