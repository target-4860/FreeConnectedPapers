<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ item.title }}</h2>
        <button class="close-button" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="info-row">
            <span class="label">来源类型:</span>
            <span class="value source-type">{{ getSourceTypeName(item.sourceType) }}</span>
          </div>
          <div class="info-row" v-if="item.authors && item.authors.length">
            <span class="label">作者:</span>
            <span class="value">{{ item.authors.join(', ') }}</span>
          </div>
          <div class="info-row" v-if="item.year">
            <span class="label">年份:</span>
            <span class="value">{{ item.year }}</span>
          </div>
          <div class="info-row" v-if="item.citations_count">
            <span class="label">引用数:</span>
            <span class="value">{{ item.citations_count }}</span>
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
              @click="searchKeyword(keyword)"
            >
              {{ keyword }}
            </span>
          </div>
        </div>
        
        <!-- 内容区域 - 根据不同类型显示不同内容 -->
        <div class="content-section">
          <!-- 教材 -->
          <div v-if="item.sourceType === 'textbook' && item.sections">
            <h3>教材章节</h3>
            <div v-for="(section, index) in item.sections" :key="index" class="section-content">
              <h4>{{ section.title }}</h4>
              <p v-html="highlightText(section.content)"></p>
            </div>
          </div>
          
          <!-- 论文 -->
          <div v-if="item.sourceType === 'paper'">
            <h3>摘要</h3>
            <p v-html="highlightText(item.abstract)"></p>
            
            <div v-if="item.journal" class="additional-info">
              <span class="label">期刊:</span>
              <span class="value">{{ item.journal }}</span>
            </div>
            
            <div v-if="item.Hyperlink" class="additional-info">
              <span class="label">论文链接:</span>
              <a :href="item.Hyperlink" target="_blank" class="paper-link">{{ item.Hyperlink }}</a>
            </div>
          </div>
          
          <!-- 电子病历 -->
          <div v-if="item.sourceType === 'emr'">
            <h3>病历摘要</h3>
            <p v-html="highlightText(item.summary)"></p>
            
            <!-- 添加图片显示区域 -->
            <div v-if="item.image_path" class="emr-image-container">
              <h4>影像资料</h4>
              <div class="image-with-annotations">
                <img :src="item.image_path" class="medical-image" alt="医学影像" />
                
                <!-- 标注区域 -->
                <div v-if="item.annotations && item.annotations.length" class="annotations-overlay">
                  <div 
                    v-for="(annotation, index) in item.annotations" 
                    :key="index"
                    class="annotation-box"
                    :class="getAnnotationClass(annotation.label)"
                    :style="{
                      left: annotation.x + '%',
                      top: annotation.y + '%',
                      width: annotation.width + '%',
                      height: annotation.height + '%'
                    }"
                    :title="annotation.label"
                  >
                    <span class="annotation-label">{{ annotation.label }}</span>
                  </div>
                </div>
              </div>
              
              <div class="image-info">
                <p v-if="item.findings"><strong>影像发现:</strong> {{ item.findings }}</p>
                <p v-if="item.impression"><strong>诊断印象:</strong> {{ item.impression }}</p>
              </div>
            </div>
            
            <div class="additional-info">
              <div v-if="item.hospital">
                <span class="label">医院:</span>
                <span class="value">{{ item.hospital }}</span>
              </div>
              <div v-if="item.patient_id">
                <span class="label">病例ID:</span>
                <span class="value">{{ item.patient_id }}</span>
              </div>
              <div v-if="item.dicom_id">
                <span class="label">影像ID:</span>
                <span class="value">{{ item.dicom_id }}</span>
              </div>
            </div>
          </div>
          
          <!-- 临床指南 -->
          <div v-if="item.sourceType === 'guideline'">
            <h3>主要建议</h3>
            
            <!-- 处理简单字符串数组格式的recommendations -->
            <ul v-if="item.recommendations && item.recommendations.length && typeof item.recommendations[0] === 'string'" class="recommendations-list">
              <li v-for="(rec, index) in item.recommendations" :key="index" v-html="highlightText(rec)"></li>
            </ul>
            
            <!-- 处理对象数组格式的recommendations -->
            <div v-else-if="item.recommendations && item.recommendations.length && typeof item.recommendations[0] === 'object'" class="structured-recommendations">
              <div v-for="(section, sectionIndex) in item.recommendations" :key="sectionIndex" class="recommendation-section">
                <h4 v-if="section.section" class="section-title">{{ section.section }}</h4>
                <ul class="section-content-list">
                  <li v-for="(contentItem, contentIndex) in section.content" :key="contentIndex" v-html="highlightText(contentItem)"></li>
                </ul>
              </div>
            </div>
            
            <div v-if="item.organization" class="additional-info">
              <span class="label">发布组织:</span>
              <span class="value">{{ item.organization }}</span>
            </div>
          </div>
        </div>
        
        <!-- 引用文献 -->
        <div class="references-section" v-if="item.references && item.references.length">
          <h3>引用文献</h3>
          <p class="references-note">该文献引用了 {{ item.references.length }} 篇相关文献</p>
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
    
    getSourceTypeName(type) {
      const sourceTypes = {
        'textbook': '教材',
        'paper': '论文',
        'emr': '电子病历',
        'guideline': '临床指南'
      };
      return sourceTypes[type] || type;
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
    
    searchKeyword(keyword) {
      // 触发关键词搜索事件
      this.$emit('search-keyword', keyword);
      this.closeModal(); // 关闭弹窗
    },
    
    getAnnotationClass(label) {
      // 根据标注类型返回不同的CSS类名
      if (!label) return 'default-annotation';
      
      const labelLower = label.toLowerCase();
      if (labelLower.includes('肺炎') || labelLower.includes('pneumonia')) {
        return 'pneumonia-annotation';
      } else if (labelLower.includes('结节') || labelLower.includes('nodule')) {
        return 'nodule-annotation';
      } else if (labelLower.includes('积液') || labelLower.includes('effusion')) {
        return 'effusion-annotation';
      } else if (labelLower.includes('气胸') || labelLower.includes('pneumothorax')) {
        return 'pneumothorax-annotation';
      } else if (labelLower.includes('肺气肿') || labelLower.includes('emphysema')) {
        return 'emphysema-annotation';
      } else {
        return 'default-annotation';
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  width: 80%;
  max-width: 900px;
  max-height: 90vh;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #888;
}

.close-button:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.info-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.info-row {
  margin-bottom: 0.5rem;
  display: flex;
}

.label {
  font-weight: 500;
  color: #666;
  width: 100px;
}

.value {
  flex: 1;
  color: #333;
}

.source-type {
  color: #2a7d8b;
  font-weight: 500;
  background-color: #e6f3f7;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  display: inline-block;
}

.keywords-section {
  margin-bottom: 1.5rem;
}

.keywords-section h3 {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
  color: #444;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  padding: 0.3rem 0.8rem;
  background-color: #f0f0f0;
  border-radius: 16px;
  font-size: 0.9rem;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}

.keyword-tag:hover {
  background-color: #2a7d8b;
  color: white;
}

.keyword-tag.highlight {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: 500;
}

.content-section {
  margin-bottom: 1.5rem;
}

.content-section h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #444;
}

.section-content {
  margin-bottom: 1.5rem;
}

.section-content h4 {
  margin-bottom: 0.5rem;
  font-size: 1rem;
  color: #555;
}

.section-content p {
  line-height: 1.6;
  color: #333;
}

.recommendations-list {
  padding-left: 1.5rem;
}

.recommendations-list li {
  margin-bottom: 0.8rem;
  line-height: 1.5;
}

.structured-recommendations {
  margin-bottom: 1.5rem;
}

.recommendation-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.1rem;
  color: #2a7d8b;
  margin-bottom: 0.5rem;
  padding-bottom: 0.2rem;
  border-bottom: 1px dashed #eee;
}

.section-content-list {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
}

.section-content-list li {
  margin-bottom: 0.6rem;
  line-height: 1.5;
}

.additional-info {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #eee;
  font-size: 0.9rem;
}

.references-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.references-section h3 {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  color: #444;
}

.references-note {
  color: #666;
  font-style: italic;
  font-size: 0.9rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.primary-button {
  padding: 0.6rem 1.2rem;
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.primary-button:hover {
  background-color: #1a6575;
}

:deep(.highlight-text) {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}

.emr-image-container {
  margin-bottom: 1.5rem;
}

.image-with-annotations {
  position: relative;
}

.medical-image {
  width: 100%;
  height: auto;
  border-radius: 4px;
}

.annotations-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.annotation-box {
  position: absolute;
  border: 2px solid #2a7d8b;
  border-radius: 4px;
  background-color: rgba(42, 125, 139, 0.2);
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.2s ease;
}

.annotation-box:hover {
  background-color: rgba(42, 125, 139, 0.4);
  z-index: 10;
}

.annotation-label {
  display: block;
  font-size: 0.8rem;
  color: #fff;
  background-color: rgba(0, 0, 0, 0.7);
  padding: 2px 4px;
  border-radius: 2px;
}

/* 不同类型的标注样式 */
.pneumonia-annotation {
  border-color: #e53935;
  background-color: rgba(229, 57, 53, 0.2);
}

.pneumonia-annotation:hover {
  background-color: rgba(229, 57, 53, 0.4);
}

.nodule-annotation {
  border-color: #43a047;
  background-color: rgba(67, 160, 71, 0.2);
}

.nodule-annotation:hover {
  background-color: rgba(67, 160, 71, 0.4);
}

.effusion-annotation {
  border-color: #1e88e5;
  background-color: rgba(30, 136, 229, 0.2);
}

.effusion-annotation:hover {
  background-color: rgba(30, 136, 229, 0.4);
}

.pneumothorax-annotation {
  border-color: #fb8c00;
  background-color: rgba(251, 140, 0, 0.2);
}

.pneumothorax-annotation:hover {
  background-color: rgba(251, 140, 0, 0.4);
}

.emphysema-annotation {
  border-color: #8e24aa;
  background-color: rgba(142, 36, 170, 0.2);
}

.emphysema-annotation:hover {
  background-color: rgba(142, 36, 170, 0.4);
}

.default-annotation {
  border-color: #2a7d8b;
  background-color: rgba(42, 125, 139, 0.2);
}

.default-annotation:hover {
  background-color: rgba(42, 125, 139, 0.4);
}

.image-info {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #eee;
}

.paper-link {
  color: #2a7d8b;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  word-break: break-all;
}

.paper-link:hover {
  color: #1a6575;
  text-decoration: underline;
}
</style> 