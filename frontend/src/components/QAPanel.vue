<template>
  <div class="qa-panel">
    <div class="qa-header">
      <h2>医学知识问答</h2>
      <div v-if="selectedItem" class="current-item">
        当前关联资料: <span>{{ selectedItem.title }}</span>
      </div>
    </div>
    
    <div class="qa-history" ref="chatHistory">
      <template v-if="conversations.length">
        <div 
          v-for="(item, index) in conversations" 
          :key="index" 
          :class="['qa-message', item.role]"
        >
          <div class="qa-content" v-html="item.role === 'assistant' ? highlightText(item.content) : item.content"></div>
          <div v-if="item.role === 'assistant' && item.citations" class="qa-citations">
            引用: {{ item.citations }}
          </div>
        </div>
      </template>
      
      <div v-else class="qa-empty-state">
        <p>您可以提问关于当前医学资料的任何问题，例如:</p>
        <ul>
          <li>高血压的诊断标准是什么？</li>
          <li>高血压的常见治疗方法有哪些？</li>
          <li>高血压与其他疾病有什么关联？</li>
        </ul>
      </div>
      
      <div v-if="isTyping" class="qa-typing">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
    
    <div class="qa-input-container">
      <textarea 
        ref="inputField"
        v-model="userInput" 
        @keydown.enter.prevent="handleSend"
        placeholder="请输入医学相关问题..."
        :disabled="isTyping"
        rows="3"
        class="qa-input"
      ></textarea>
      <button 
        @click="handleSend" 
        class="qa-send-button"
        :disabled="isTyping || !userInput.trim()"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QAPanel',
  props: {
    selectedItem: {
      type: Object,
      default: null
    },
    searchQuery: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      userInput: '',
      conversations: [],
      isTyping: false
    }
  },
  watch: {
    selectedItem(newItem, oldItem) {
      if (newItem && (!oldItem || newItem.id !== oldItem.id)) {
        // 当选择的项目改变时，添加一条系统消息
        this.conversations.push({
          role: 'system',
          content: `已切换至：${newItem.title}`
        });
        this.scrollToBottom();
      }
    }
  },
  methods: {
    handleSend() {
      if (!this.userInput.trim() || this.isTyping) return;
      
      // 添加用户问题到对话记录
      this.conversations.push({
        role: 'user',
        content: this.userInput
      });
      
      const question = this.userInput;
      this.userInput = '';
      this.isTyping = true;
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
      
      // 模拟AI回答（实际项目中应替换为真实API调用）
      setTimeout(() => {
        this.simulateResponse(question);
      }, 1000);
    },
    
    simulateResponse(question) {
      let response = '';
      let citations = '';
      
      if (!this.selectedItem) {
        response = "请先选择一项医学资料，以便我能更准确地回答您的问题。";
      } else {
        // 根据问题内容和选中的项目生成模拟回答
        const item = this.selectedItem;
        const sourceType = item.sourceType;
        
        if (question.includes('诊断') || question.includes('标准')) {
          if (sourceType === 'guideline') {
            response = `根据《${item.title}》，高血压的诊断标准为：非同日3次测量，收缩压≥140mmHg和/或舒张压≥90mmHg。对于老年人、糖尿病患者和慢性肾病患者，诊断标准可能有所调整。`;
            citations = "引用自指南诊断章节";
          } else if (sourceType === 'textbook') {
            response = `《${item.title}》中指出，高血压的诊断需要基于多次血压测量的结果，通常定义为收缩压≥140mmHg和/或舒张压≥90mmHg。需要注意的是，诊断高血压前应排除"白大衣高血压"的可能。`;
            citations = "引用自教材第5章";
          } else {
            response = `关于高血压的诊断标准，一般参考最新的高血压指南。目前普遍接受的标准是：非同日3次测量，收缩压≥140mmHg和/或舒张压≥90mmHg。`;
          }
        } else if (question.includes('治疗') || question.includes('用药')) {
          if (sourceType === 'guideline') {
            response = `《${item.title}》推荐的高血压治疗包括：1) 生活方式干预：减少钠盐摄入、增加体力活动、限制饮酒、戒烟等；2) 药物治疗：常用药物包括利尿剂、β受体阻滞剂、钙拮抗剂、ACEI/ARB等。对于不同患者，应根据年龄、合并症等因素选择合适的药物。`;
            citations = "引用自指南治疗章节";
          } else if (sourceType === 'paper') {
            response = `根据《${item.title}》的研究，高血压治疗的最新趋势是强调个体化治疗策略，根据患者的年龄、合并症、靶器官损害情况等因素选择最合适的药物组合。研究表明，早期联合治疗可能优于单药递增治疗策略。`;
            citations = "引用自论文结果与讨论部分";
          } else {
            response = `高血压的治疗包括非药物治疗和药物治疗。非药物治疗包括减少钠盐摄入、增加体力活动、限制饮酒、戒烟等；药物治疗常用的五类降压药包括利尿剂、β受体阻滞剂、钙拮抗剂、ACEI和ARB。`;
          }
        } else if (question.includes('并发症') || question.includes('风险')) {
          if (sourceType === 'emr') {
            response = `根据《${item.title}》的数据分析，高血压患者常见的并发症包括冠心病、心力衰竭、脑卒中、肾功能不全等。数据显示，血压控制不良的患者并发症发生率显著高于血压控制良好的患者。`;
            citations = "引用自电子病历分析结果";
          } else {
            response = `高血压是心脑血管疾病的主要危险因素，长期血压升高可导致心、脑、肾等靶器官损害。常见并发症包括冠心病、心力衰竭、脑卒中、肾功能不全等。良好控制血压可显著降低并发症风险。`;
          }
        } else {
          response = `关于"${item.title}"中的${question}，这是一个很好的问题。作为一份${this.getSourceTypeName(sourceType)}资料，它提供了关于高血压的重要信息。建议您查阅原文以获取更详细的内容，或者尝试提问更具体的问题，如高血压的诊断标准、治疗方法或并发症等。`;
        }
      }
      
      // 添加回答到对话记录
      this.conversations.push({
        role: 'assistant',
        content: response,
        citations: citations
      });
      
      this.isTyping = false;
      
      // 滚动到底部
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    
    scrollToBottom() {
      const container = this.$refs.chatHistory;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
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
    
    highlightText(text) {
      if (!text || !this.searchQuery) return text;
      
      const regex = new RegExp(`(${this.searchQuery})`, 'gi');
      return text.replace(regex, '<span class="highlight-text">$1</span>');
    }
  },
  mounted() {
    // 页面加载时显示欢迎消息
    this.conversations.push({
      role: 'assistant',
      content: '欢迎使用医学知识问答系统！请选择左侧资料或在知识图谱中点击节点，然后提问相关问题。'
    });
  }
}
</script>

<style scoped>
.qa-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
}

.qa-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  background-color: #f0f0f0;
}

.qa-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #444;
  margin: 0;
  margin-bottom: 0.5rem;
}

.current-item {
  font-size: 0.8rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-item span {
  font-weight: 500;
  color: #2a7d8b;
}

.qa-history {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qa-message {
  max-width: 85%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  position: relative;
}

.qa-message.user {
  align-self: flex-end;
  background-color: #e7f3f5;
  color: #333;
}

.qa-message.assistant {
  align-self: flex-start;
  background-color: #f5f5f5;
  color: #333;
}

.qa-message.system {
  align-self: center;
  background-color: #f0f0f0;
  color: #666;
  font-size: 0.8rem;
  padding: 0.5rem 0.8rem;
  border-radius: 12px;
}

.qa-content {
  word-break: break-word;
  line-height: 1.4;
}

.qa-citations {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #888;
  font-style: italic;
}

.qa-empty-state {
  color: #888;
  font-size: 0.9rem;
  text-align: center;
  padding: 1rem;
}

.qa-empty-state ul {
  text-align: left;
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.qa-empty-state li {
  margin-bottom: 0.3rem;
}

.qa-typing {
  align-self: flex-start;
  margin-top: 0.5rem;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #aaa;
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}

.qa-input-container {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #eee;
  background-color: #f9f9f9;
}

.qa-input {
  flex: 1;
  resize: none;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  padding: 0.6rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.qa-input:focus {
  outline: none;
  border-color: #2a7d8b;
}

.qa-send-button {
  background-color: #2a7d8b;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  padding: 0 1.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.qa-send-button:hover {
  background-color: #1a6575;
}

.qa-send-button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

:deep(.highlight-text) {
  background-color: #ffecb3;
  color: #e65100;
  font-weight: bold;
  padding: 0 2px;
  border-radius: 2px;
}
</style> 