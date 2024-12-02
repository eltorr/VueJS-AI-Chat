<template>
  <div class="app-container">
    <div class="sidebar">
      <div class="chat-header">
        <h1>Omni Chat</h1>
        <button class="clear-chat-btn" @click="clearChat" :disabled="!messages.length">
          Clear Chat 🗑️
        </button>
      </div>
      <div class="model-controls">
        <div class="provider-select">
          <label>
            <input type="radio" v-model="provider" value="openai"> OpenAI
          </label>
          <label>
            <input type="radio" v-model="provider" value="ollama"> Ollama
          </label>
        </div>
        <ModelSelector 
          :provider="provider" 
          @model-selected="handleModelSelect" 
        />
      </div>
    </div>
    
    <div class="chat-container">
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
              <div v-if="message.role === 'assistant'" class="model-tag">
                {{ message.model || 'OpenAI' }}
              </div>
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
          <label v-if="modelSupportsVision" class="upload-button" :class="{ 'has-image': selectedImage }">
            <input 
              type="file" 
              accept="image/*" 
              @change="handleImageUpload" 
              class="hidden"
            >
            {{ selectedImage ? '📸' : '📤' }}
          </label>
          
          <div v-if="currentSuggestion" class="suggestion-bubble" @click="applySuggestion">
            <div class="suggestion-content">
              💡 {{ currentSuggestion }}
            </div>
          </div>
          
          <textarea 
            v-model="newMessage" 
            @keyup.enter.exact="sendMessage" 
            @input="handleInput"
            placeholder="Type your message..."
            rows="1"
            ref="messageInput"
          ></textarea>
          
          <div v-if="selectedImage" class="image-preview">
            <img :src="selectedImageUrl" alt="Selected image">
            <button class="remove-image" @click="removeImage">×</button>
          </div>
          
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ModelSelector from './ModelSelector.vue'

const messages = ref([])
const newMessage = ref('')
const messageInput = ref(null)
const messageContainer = ref(null)
const isLoading = ref(false)
const isTyping = ref(false)
const selectedImage = ref(null)
const selectedImageUrl = ref(null)
const provider = ref('openai')
const selectedModel = ref(null)
const modelSupportsVision = ref(false)
const currentSuggestion = ref(null)
const typingTimeout = ref(null)

const handleInput = async (event) => {
  const textarea = event.target
  textarea.style.height = 'auto'
  textarea.style.height = textarea.scrollHeight + 'px'

  if (typingTimeout.value) clearTimeout(typingTimeout.value)

  // Clear suggestion if input is empty
  if (!newMessage.value.trim()) {
    currentSuggestion.value = null
    return
  }

  typingTimeout.value = setTimeout(async () => {
    try {
      console.log('Requesting suggestion...')  // Debug log
      const response = await axios.post('http://localhost:5001/api/ollama/chat', {
        messages: [
          {
            role: 'user',
            content: `Given this start of a message: "${newMessage.value.trim()}", suggest a natural completion. Keep it brief and natural, do no answer it to it, you just complete it.`
          }
        ],
        model: 'llama3.2:latest' 
      })

      console.log('Suggestion response:', response.data)  // Debug log

      if (response.data && response.data.message) {
        currentSuggestion.value = response.data.message
      }
    } catch (error) {
      console.error('Suggestion error:', error)
      currentSuggestion.value = null
    }
  }, 500)
}

const applySuggestion = () => {
  if (currentSuggestion.value) {
    newMessage.value = currentSuggestion.value
    currentSuggestion.value = null
    sendMessage()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    selectedImageUrl.value = URL.createObjectURL(file)
  }
}

const removeImage = () => {
  if (selectedImageUrl.value) {
    URL.revokeObjectURL(selectedImageUrl.value)
  }
  selectedImage.value = null
  selectedImageUrl.value = null
}

const sendMessage = async () => {
  if ((!newMessage.value.trim() && !selectedImage.value) || isLoading.value) return
  
  currentSuggestion.value = null // Clear any existing suggestions
  
  const userMessage = {
    role: 'user',
    content: newMessage.value.trim()
  }

  if (selectedImage.value && modelSupportsVision.value) {
    const reader = new FileReader()
    reader.onload = async () => {
      const base64Image = reader.result.split(',')[1]
      userMessage.images = [base64Image]
      await sendMessageWithImage(userMessage)
    }
    reader.readAsDataURL(selectedImage.value)
  } else {
    await sendMessageWithImage(userMessage)
  }
}

const sendMessageWithImage = async (userMessage) => {
  messages.value.push(userMessage)
  newMessage.value = ''
  isLoading.value = true
  isTyping.value = false
  
  try {
    const endpoint = provider.value === 'ollama' ? '/api/ollama/chat' : '/api/chat'
    
    const formattedMessages = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content,
      images: msg.images || []
    }))

    const payload = {
      messages: formattedMessages,
      model: selectedModel.value
    }
    
    console.log('Sending payload:', payload)
    
    const response = await axios.post(`http://localhost:5001${endpoint}`, payload)

    if (response.data && response.data.message) {
      messages.value.push({
        role: 'assistant',
        content: response.data.message,
        model: selectedModel.value
      })
      
      if (selectedImage.value) {
        removeImage()
      }
    } else {
      throw new Error('Invalid response format')
    }
  } catch (error) {
    console.error('Chat error:', error)
    let errorMessage = 'Sorry, I encountered an error. Please try again.'
    
    if (error.response?.data?.detail) {
      errorMessage = `Error: ${error.response.data.detail}`
    }
    
    messages.value.push({
      role: 'assistant',
      content: errorMessage
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const handleModelSelect = (modelInfo) => {
  selectedModel.value = modelInfo.name
  modelSupportsVision.value = modelInfo.supportsVision
  if (!modelSupportsVision.value) {
    removeImage()
  }
}

watch(provider, () => {
  modelSupportsVision.value = false
  removeImage()
})

onMounted(() => {
  if (messageInput.value) {
    messageInput.value.focus()
  }
})

watch(messages, async () => {
  await scrollToBottom()
}, { deep: true })

const clearChat = () => {
  messages.value = []
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  font-family: 'Quicksand', sans-serif;
}

.sidebar {
  width: 280px;
  background: var(--bg-primary);
  padding: 24px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden;
  background: var(--bg-primary);
}

.model-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-select {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.provider-select label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--text-primary);
}

.provider-select label:hover {
  background: var(--bg-secondary);
}

.provider-select input[type="radio"] {
  accent-color: var(--accent-color);
}

.chat-header {
  text-align: left;
  margin-bottom: 20px;
}

.chat-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  font-weight: 700;
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
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
  display: flex;
  animation: fadeIn 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 4px 0;
  margin: 8px 0;
}

.message-avatar {
  font-size: 1.5rem;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-bubble {
  padding: 16px 24px;
  border-radius: 20px;
  max-width: calc(100% - 100px);
  transition: all 0.3s ease;
  font-size: 1.1rem;
  line-height: 1.6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--message-user), #60a5fa);
  color: white;
  margin-left: auto;
  transform-origin: right bottom;
  font-family: 'Quicksand', sans-serif !important;
  font-weight: 500;
}

.message.assistant .message-bubble {
  background: var(--message-assistant);
  color: var(--text-primary);
  transform-origin: left bottom;
  font-family: 'Quicksand', sans-serif !important;
  font-weight: 500;
}

.chat-input {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

textarea {
  width: 100%;
  padding: 12px 20px;
  border: 2px solid var(--border-color);
  border-radius: 16px;
  resize: none;
  font-family: 'Quicksand', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1.1rem;
  line-height: 1.6;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 48px;
  max-height: 150px;
  overflow-y: auto;
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
  height: 48px;
  min-width: 48px;
  padding: 0;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 600;
  font-family: 'Quicksand', sans-serif;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

button:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(96, 165, 250, 0.2);
}

.send-icon {
  font-size: 1.5rem;
  transform: rotate(-45deg);
  display: inline-block;
  transition: transform 0.3s ease;
}

button:hover .send-icon {
  transform: rotate(-45deg) translateX(2px);
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

<style>
/* Global styles for markdown content within messages */
.message.user .markdown-content,
.message.user .markdown-content p {
  font-family: 'Quicksand', sans-serif !important;
  font-size: 1.1rem !important;
}

.message.assistant .markdown-content,
.message.assistant .markdown-content p {
  font-family: 'Quicksand', sans-serif !important;
  font-size: 1.1rem !important;
}

/* Keep special styling for code and quotes */
.message.assistant .markdown-content pre code {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9rem !important;
}

.message.assistant .markdown-content blockquote {
  font-family: 'Caveat', cursive !important;
  font-size: 1.3em !important;
}
</style>

<style>
.model-controls {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: fadeInDown 0.8s ease-out;
}

.provider-select {
  display: flex;
  gap: 20px;
  padding: 8px;
  margin-bottom: 12px;
}

.provider-select label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-primary);
  font-family: 'Quicksand', sans-serif;
  font-size: 1.1rem;
}

.provider-select input[type="radio"] {
  cursor: pointer;
}
</style>

<style scoped>
.model-tag {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-family: 'JetBrains Mono', monospace;
  padding: 2px 8px;
  background: var(--bg-primary);
  border-radius: 12px;
  display: inline-block;
  opacity: 0.8;
}

.dark-mode .model-tag {
  background: var(--bg-secondary);
}
</style>

<style scoped>
/* Mobile responsiveness */
@media (max-width: 768px) {
  .chat-input {
    padding: 12px;
    gap: 12px;
  }
  
  textarea {
    padding: 12px 16px;
  }
  
  button {
    min-width: 48px;
  }
}
</style>

<style scoped>
.upload-button {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.5rem;
  opacity: 0.7;
  transition: all 0.3s ease;
  z-index: 2;
}

.upload-button:hover {
  opacity: 1;
}

.upload-button.has-image {
  color: var(--accent-color);
}

.upload-button input {
  display: none;
}

.image-preview {
  position: fixed;
  bottom: 100px;
  right: 24px;
  max-width: 200px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  padding: 0;
  font-size: 18px;
}

.remove-image:hover {
  background: rgba(0, 0, 0, 0.7);
}

textarea {
  padding-left: 48px;  /* Make room for upload button */
}

.hidden {
  display: none;
}
</style>

<style scoped>
/* Mobile responsiveness */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    padding: 16px;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .chat-container {
    padding: 16px;
  }
}
</style>

<style scoped>
/* Update styles for suggestion bubble */
.suggestion-bubble {
  position: absolute;
  bottom: calc(100% + 12px); /* Slightly more space above the input */
  left: 48px;
  background: var(--bg-secondary);
  border: 2px solid var(--accent-color); /* Thicker border */
  border-radius: 24px; /* More rounded corners */
  padding: 12px 20px; /* Larger padding */
  cursor: pointer;
  transition: all 0.2s ease;
  animation: bubbleIn 0.3s ease-out;
  max-width: calc(100% - 96px);
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* Add shadow for depth */
}

.suggestion-bubble:hover {
  transform: translateY(-2px);
  background: var(--accent-color);
  color: white;
}

.suggestion-bubble::after {
  content: '';
  position: absolute;
  bottom: -8px; /* Adjust position for larger bubble */
  left: 24px;
  width: 16px; /* Larger arrow */
  height: 16px; /* Larger arrow */
  background: inherit;
  border-right: 2px solid var(--accent-color); /* Thicker arrow border */
  border-bottom: 2px solid var(--accent-color); /* Thicker arrow border */
  transform: rotate(45deg);
}

.suggestion-bubble:hover::after {
  border-color: var(--accent-color);
}

.suggestion-content {
  font-size: 1rem; /* Slightly larger text */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes bubbleIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

<style scoped>
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.clear-chat-btn {
  padding: 8px 16px;
  font-size: 0.9rem;
  height: auto;
  min-width: auto;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  opacity: 0.8;
}

.clear-chat-btn:hover:not(:disabled) {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
  transform: translateY(-2px);
}

.clear-chat-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>