<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1>AI Chat Assistant</h1>
      <div class="header-animation"></div>
    </div>
    <div class="chat-messages" ref="messageContainer">
      <div v-for="(message, index) in messages" 
           :key="index" 
           :class="['message', message.role]"
           :style="{ animationDelay: `${index * 0.1}s` }">
        <div class="message-content">
          <div class="message-avatar">
            {{ message.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-bubble">
            <MarkdownRenderer 
              :content="message.content" 
              :isLoading="isLoading && index === messages.length - 1" 
            />
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <div class="input-wrapper">
        <textarea 
          v-model="newMessage" 
          @keyup.enter.exact="sendMessage"
          @input="handleInput"
          placeholder="Type your message..."
          rows="1"
          ref="messageInput"
        ></textarea>
        <div class="typing-indicator" v-if="isTyping">
          <span></span><span></span><span></span>
        </div>
      </div>
      <button @click="sendMessage" :disabled="isLoading">
        <span class="button-content">
          <span v-if="isLoading" class="loader"></span>
          <span v-else class="send-icon">↗</span>
        </span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useAIChat } from '@/services/aiChat'
import MarkdownRenderer from './MarkdownRenderer.vue'

export default {
  name: 'ChatInterface',
  components: {
    MarkdownRenderer
  },
  setup() {
    const messages = ref([])
    const newMessage = ref('')
    const isLoading = ref(false)
    const isTyping = ref(false)
    const messageContainer = ref(null)
    const { sendChatMessage } = useAIChat()
    let typingTimeout = null

    const handleInput = (e) => {
      // Auto-grow textarea
      const textarea = e.target;
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';

      // Handle typing indicator
      isTyping.value = true;
      if (typingTimeout) clearTimeout(typingTimeout);
      
      typingTimeout = setTimeout(() => {
        isTyping.value = false;
      }, 1000);
    }

    const scrollToBottom = async () => {
      await nextTick()
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight
      }
    }

    const sendMessage = async () => {
      if (!newMessage.value.trim() || isLoading.value) return

      const userMessage = {
        role: 'user',
        content: newMessage.value.trim()
      }
      
      messages.value.push(userMessage)
      newMessage.value = ''
      isLoading.value = true
      isTyping.value = false
      
      try {
        const response = await sendChatMessage([...messages.value])
        messages.value.push({
          role: 'assistant',
          content: response.message
        })
      } catch (error) {
        console.error('Error:', error)
      } finally {
        isLoading.value = false
        scrollToBottom()
      }
    }

    onMounted(() => {
      messages.value = []
    })

    return {
      messages,
      newMessage,
      isLoading,
      isTyping,
      messageContainer,
      sendMessage,
      handleInput
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden;
  font-family: var(--font-primary);
}

.chat-header {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
}

.chat-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin: 0;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(45deg, var(--accent-color), #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: fadeInDown 0.8s ease-out;
}

.header-animation {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
  animation: headerSlide 2s infinite;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 24px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--accent-color);
  border-radius: 3px;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.message {
  margin-bottom: 24px;
  animation: messageSlide 0.5s ease-out forwards;
  opacity: 0;
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.message-avatar {
  font-size: 1.5rem;
  min-width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.message-avatar:hover {
  transform: scale(1.1) rotate(5deg);
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 18px;
  max-width: calc(100% - 80px);
  transition: transform 0.3s ease;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--message-user), #60a5fa);
  color: white;
  margin-left: auto;
  transform-origin: right bottom;
}

.message.assistant .message-bubble {
  background: var(--message-assistant);
  color: var(--text-primary);
  transform-origin: left bottom;
}

.message-bubble:hover {
  transform: translateY(-2px);
}

.chat-input {
  display: flex;
  gap: 16px;
  background: var(--bg-secondary);
  padding: 24px;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.input-wrapper {
  position: relative;
  flex: 1;
}

textarea {
  width: 100%;
  padding: 16px 20px;
  border: 2px solid var(--border-color);
  border-radius: 16px;
  resize: none;
  font-family: var(--font-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.6;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 60px;
}

textarea:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.1);
}

.typing-indicator {
  position: absolute;
  bottom: 12px;
  left: 20px;
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--accent-color);
  animation: typingBounce 0.8s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

button {
  padding: 16px 32px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 600;
  font-family: var(--font-primary);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  min-width: 120px;
}

button:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
  transform: none;
}

button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(96, 165, 250, 0.2);
}

.send-icon {
  font-size: 1.5rem;
  transform: rotate(-45deg);
  display: inline-block;
}

.loader {
  width: 24px;
  height: 24px;
  border: 3px solid #ffffff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typingBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes headerSlide {
  0% { transform: translateX(-150%); }
  50% { transform: translateX(50%); }
  100% { transform: translateX(150%); }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>