<template>
  <div class="qa-panel">
    <div class="qa-header">
      <h2>论文知识问答</h2>
      <div v-if="selectedPaper" class="current-paper">
        当前关联论文: <span>{{ selectedPaper.title }}</span>
      </div>
    </div>
    
    <div class="qa-history" ref="chatHistory">
      <template v-if="conversations.length">
        <div 
          v-for="(item, index) in conversations" 
          :key="index" 
          :class="['qa-message', item.role]"
        >
          <div class="qa-content">{{ item.content }}</div>
          <div v-if="item.role === 'assistant' && item.citations" class="qa-citations">
            引用: {{ item.citations }}
          </div>
        </div>
      </template>
      
      <div v-else class="qa-empty-state">
        <p>您可以提问关于当前论文的任何问题，例如:</p>
        <ul>
          <li>这篇论文的主要贡献是什么？</li>
          <li>论文中提到的关键技术有哪些？</li>
          <li>与其他相关工作有何区别？</li>
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
        placeholder="请输入论文相关问题..."
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
    selectedPaper: {
      type: Object,
      default: null
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
    selectedPaper(newPaper, oldPaper) {
      if (newPaper && (!oldPaper || newPaper.id !== oldPaper.id)) {
        // 当选择的论文改变时，添加一条系统消息
        this.conversations.push({
          role: 'system',
          content: `已切换至论文：${newPaper.title}`
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
      
      if (!this.selectedPaper) {
        response = "请先选择一篇论文，以便我能更准确地回答您的问题。";
      } else {
        // 根据问题内容和选中的论文生成模拟回答
        if (question.includes('贡献') || question.includes('重要性')) {
          response = `${this.selectedPaper.title} 的主要贡献在于提出了一种新的${this.selectedPaper.title.includes('Diffusion') ? '扩散模型' : '生成方法'}，能够实现高质量的图像生成。与之前的方法相比，该模型能够更好地控制生成过程，并且在图像质量和多样性方面取得了显著进步。`;
          citations = "引用自论文摘要和第3节方法部分";
        } else if (question.includes('方法') || question.includes('技术')) {
          response = `该论文采用了${this.selectedPaper.title.includes('CLIP') ? 'CLIP潜在空间编码' : '扩散模型'} 作为核心技术，通过${this.selectedPaper.title.includes('Text') ? '文本条件引导' : '多阶段生成过程'} 来控制图像生成过程。这种方法能够有效利用大规模预训练模型的知识，实现高质量、可控的图像生成。`;
          citations = "引用自论文第2节相关工作和第4节实验结果";
        } else if (question.includes('结果') || question.includes('效果')) {
          response = `根据论文第5节的实验结果，该方法在MS-COCO等数据集上的FID得分为${Math.floor(Math.random() * 10 + 5)}，优于此前的最佳方法。人类评估实验也表明，该方法生成的图像在视觉质量和文本对齐性方面均取得了显著提升。`;
          citations = "引用自论文第5节实验评估部分";
        } else {
          response = `关于"${this.selectedPaper.title}"，您的问题涉及到的内容可能需要更深入地分析论文。该论文由${this.selectedPaper.authors.join(', ')}在${this.selectedPaper.year}年发表，已被引用${this.selectedPaper.citations_count || 0}次，是${this.selectedPaper.title.includes('Diffusion') ? '扩散模型' : '图像生成'}领域的重要研究。建议您查阅原论文以获取更详细信息。`;
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
    }
  },
  mounted() {
    // 页面加载时显示欢迎消息
    this.conversations.push({
      role: 'assistant',
      content: '欢迎使用论文知识问答系统！请选择左侧论文或在知识图谱中点击节点，然后提问关于论文的问题。'
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

.current-paper {
  font-size: 0.8rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-paper span {
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
</style> 