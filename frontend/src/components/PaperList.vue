<template>
  <div class="paper-list">
    <div class="paper-list-header">
      <h2>相关论文</h2>
    </div>
    
    <div class="paper-list-content">
      <div 
        v-for="paper in papers" 
        :key="paper.id" 
        class="paper-item" 
        :class="{ 'selected': selectedPaper && selectedPaper.id === paper.id }"
        @click="selectPaper(paper)"
      >
        <div class="paper-title">{{ paper.title }}</div>
        <div class="paper-authors">{{ formatAuthors(paper.authors) }}</div>
        <div class="paper-meta">
          <span class="paper-year">{{ paper.year }}</span>
          <span class="paper-citations" v-if="paper.citations_count">
            引用数: {{ paper.citations_count }}
          </span>
        </div>
      </div>
      
      <div v-if="papers.length === 0" class="no-papers">
        没有找到相关论文，请尝试其他关键词
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaperList',
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
  methods: {
    selectPaper(paper) {
      this.$emit('select-paper', paper);
    },
    formatAuthors(authors) {
      if (!authors || authors.length === 0) return '';
      if (authors.length === 1) return authors[0];
      return authors.slice(0, 2).join(', ') + (authors.length > 2 ? ' 等' : '');
    }
  }
}
</script>

<style scoped>
.paper-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fafafa;
}

.paper-list-header {
  padding: 1rem;
  background-color: #f0f0f0;
  border-bottom: 1px solid #e0e0e0;
}

.paper-list-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #444;
  margin: 0;
}

.paper-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.paper-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.paper-item:hover {
  background-color: #f0f7f9;
}

.paper-item.selected {
  background-color: #e6f3f7;
  border-left: 4px solid #2a7d8b;
}

.paper-title {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-authors {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.4rem;
}

.paper-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #888;
}

.paper-year {
  font-weight: 500;
}

.paper-citations {
  color: #2a7d8b;
}

.no-papers {
  padding: 2rem;
  text-align: center;
  color: #888;
  font-style: italic;
}
</style> 