<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ item.title }}</h2>
        <button class="close-button" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="info-type">{{ getSourceTypeName(item.sourceType) }}</div>
          <div class="info-meta">
            <span v-if="item.authors"><strong>作者:</strong> {{ formatAuthors(item.authors) }}</span>
            <span v-if="item.year"><strong>年份:</strong> {{ item.year }}</span>
            <span v-if="item.publisher"><strong>出版社:</strong> {{ item.publisher }}</span>
            <span v-if="item.journal"><strong>期刊:</strong> {{ item.journal }}</span>
            <span v-if="item.hospital"><strong>医院:</strong> {{ item.hospital }}</span>
            <span v-if="item.organization"><strong>组织:</strong> {{ item.organization }}</span>
          </div>
        </div>
        
        <!-- 关键词 -->
        <div class="keywords-section" v-if="item.keywords && item.keywords.length">
          <h3>关键词</h3>
          <div class="keywords-list">
            <span 
              v-for="(keyword, index) in item.keywords" 
              :key="index" 
              class="keyword-tag"
              :class="{ 'highlight': isSearchKeyword(keyword) }"
            >
              {{ keyword }}
            </span>
          </div>
        </div>
        
        <!-- 摘要/简介 -->
        <div class="abstract-section" v-if="item.abstract || item.summary">
          <h3>摘要</h3>
          <p v-html="highlightText(item.abstract || item.summary)"></p>
        </div>
        
        <!-- 章节内容 -->
        <div class="sections-section" v-if="item.sections && item.sections.length">
          <h3>相关章节</h3>
          <div 
            v-for="(section, index) in item.sections" 
            :key="index"
            class="section-item"
          >
            <h4>{{ section.title }}</h4>
            <p v-html="highlightText(section.content)"></p>
          </div>
        </div>
        
        <!-- 建议/推荐 -->
        <div class="recommendations-section" v-if="item.recommendations && item.recommendations.length">
          <h3>主要建议</h3>
          <ul class="recommendations-list">
            <li 
              v-for="(rec, index) in item.recommendations" 
              :key="index"
              v-html="highlightText(rec)"
            ></li>
          </ul>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="primary-button" @click="closeModal">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DetailModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    item: {
      type: Object,
      default: () => ({})
    },
    searchQuery: {
      type: String,
      default: ''
    }
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    
    formatAuthors(authors) {
      if (!authors || authors.length === 0) return '';
      return authors.join(', ');
    },
    
    getSourceTypeName(type) {
      const sourceTypes = {
        'textbook': '教材',
        'paper': '论文',
        'emr': '电子病历',
        'guideline': '临床指南'
      };
      return sourceTypes[type] || '未知来源';
    },
    
    isSearchKeyword(keyword) {
      if (!this.searchQuery) return false;
      return keyword.toLowerCase().includes(this.searchQuery.toLowerCase());
    },
    
    highlightText(text) {
      if (!text || !this.searchQuery) return text;
      
      const regex = new RegExp(`(${this.searchQuery})`, 'gi');
      return text.replace(regex, '<span class="highlight-text">$1</span>');
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9f9f9;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #777;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.info-section {
  margin-bottom: 1.5rem;
}

.info-type {
  display: inline-block;
  padding: 0.3rem 0.6rem;
  background-color: #2a7d8b;
  color: white;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.8rem;
}

.info-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
  color: #555;
}

.keywords-section {
  margin-bottom: 1.5rem;
}

.keywords-section h3,
.abstract-section h3,
.sections-section h3,
.recommendations-section h3 {
  font-size: 1.1rem;
  color: #444;
  margin-bottom: 0.8rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background-color: #f0f0f0;
  padding: 0.3rem 0.6rem;
  border-radius: 16px;
  font-size: 0.85rem;
  color: #555;
}

.keyword-tag.highlight {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: 500;
}

.abstract-section {
  margin-bottom: 1.5rem;
}

.abstract-section p {
  line-height: 1.6;
  color: #333;
}

.sections-section {
  margin-bottom: 1.5rem;
}

.section-item {
  margin-bottom: 1.2rem;
  padding-bottom: 1.2rem;
  border-bottom: 1px dashed #eee;
}

.section-item:last-child {
  border-bottom: none;
}

.section-item h4 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: #444;
}

.section-item p {
  line-height: 1.6;
  color: #333;
}

.recommendations-list {
  padding-left: 1.5rem;
}

.recommendations-list li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.primary-button {
  padding: 0.5rem 1.2rem;
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.primary-button:hover {
  background-color: #1a6575;
}

/* 高亮文本样式 */
:deep(.highlight-text) {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}
</style> 