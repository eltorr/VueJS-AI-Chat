<template>
  <div class="app-container">
    <div class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="sidebar-content">
        <div class="chat-header">
          <h1>Omni Chat</h1>
        </div>
        <div class="model-controls">
          <div class="provider-carousel">
            <div class="carousel-viewport">
              <div class="carousel-track" ref="carouselTrack">
                <div class="provider-card" 
                     v-for="(item, index) in providers" 
                     :key="index"
                     :class="{ active: provider === item.id }"
                     @click="selectProvider(item.id)"
                     :style="getCardStyle(index)">
                  <div class="provider-content">
                    <div class="provider-icon" v-html="item.icon"></div>
                    <div class="provider-name">{{ item.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="models-list">
            <ModelSelector 
              :provider="provider" 
              @model-selected="handleModelSelect" 
            />
          </div>
          <div class="carousel-bottom-nav">
            <button @click="rotateCarousel('prev')" aria-label="Previous">‹</button>
            <button @click="rotateCarousel('next')" aria-label="Next">›</button>
          </div>
        </div>
        <div class="sidebar-footer">
          <button class="clear-chat-btn" @click="clearChat" :disabled="!messages.length">
            Clear Chat 🗑️
          </button>
        </div>
      </div>
      
      <button class="sidebar-toggle" @click="toggleSidebar">
        <span class="toggle-icon">{{ isSidebarCollapsed ? '›' : '‹' }}</span>
      </button>
    </div>
    
    <div class="chat-container">
      <div class="sidebar-title">Omni Chat</div>
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
              <div class="message-actions">
                <button class="action-btn" @click="copyContent(message)" :title="hasImage(message.content) ? 'Copy image' : 'Copy'">
                  <svg class="copy-icon" viewBox="0 0 24 24" width="16" height="16">
                    <path fill="none" stroke="var(--text-primary)" stroke-width="2" d="M8 4v12a2 2 0 002 2h8a2 2 0 002-2V7.242a2 2 0 00-.602-1.43L16.083 2.57A2 2 0 0014.685 2H10a2 2 0 00-2 2z"/>
                    <path fill="none" stroke="var(--text-primary)" stroke-width="2" d="M16 18v2a2 2 0 01-2 2H6a2 2 0 01-2-2V9a2 2 0 012-2h2"/>
                  </svg>
                </button>
              </div>
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
            @paste="handlePaste"
            :placeholder="modelSupportsVision ? 'Type your message or paste an image...' : 'Type your message...'"
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
            <span v-if="isLoading" class="electric-loader">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path class="bolt" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </span>
            <span v-else class="send-icon">↗</span>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import axios from 'axios'
import MarkdownRenderer from './MarkdownRenderer.vue'
import ModelSelector from './ModelSelector.vue'
import OpenAiIcon from '../assets/openai.svg'
import OllamaIcon from '../assets/ollama.svg'

const messages = ref([])
const newMessage = ref('')
const messageInput = ref(null)
const messageContainer = ref(null)
const isLoading = ref(false)
const isTyping = ref(false)
const selectedImage = ref(null)
const selectedImageUrl = ref(null)
const provider = ref('openai')
const selectedModel = ref({
  name: '',
  supportsVision: false
})
const modelSupportsVision = ref(false)
const currentSuggestion = ref(null)
const typingTimeout = ref(null)
const isSidebarCollapsed = ref(false)

const providers = [
  { 
    id: 'openai', 
    name: 'OpenAI', 
    icon: `<img src="${OpenAiIcon}" alt="OpenAI" width="24" height="24">`
  },
  { 
    id: 'ollama', 
    name: 'Ollama', 
    icon: `<img src="${OllamaIcon}" alt="Ollama" width="24" height="24">`
  }
];

const carouselTrack = ref(null);
const rotation = ref(0);
const CARD_ANGLE = 360 / providers.length;

const getCardStyle = (index) => {
  const angle = (CARD_ANGLE * index) - rotation.value;
  const radius = 100;
  const x = Math.sin(angle * Math.PI / 180) * radius;
  const z = Math.cos(angle * Math.PI / 180) * radius - radius;
  
  const opacity = z < -radius/2 ? 0.15 : (z < 0 ? 0.3 : 0.8);
  
  return {
    transform: `translateX(${x}px) translateZ(${z}px) rotateY(${angle}deg)`,
    zIndex: z < -radius/2 ? -1 : 1,
    opacity: opacity
  };
};

const selectProvider = (id) => {
  const currentIndex = providers.findIndex(p => p.id === provider.value);
  const newIndex = providers.findIndex(p => p.id === id);
  const diff = newIndex - currentIndex;
  
  rotation.value += diff * CARD_ANGLE;
  provider.value = id;
};

// Update the handleWheel function and add event listeners
const handleWheel = (e) => {
  e.preventDefault();
  if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
    rotation.value += Math.sign(e.deltaX) * (CARD_ANGLE / 4);
  } else {
    rotation.value += Math.sign(e.deltaY) * (CARD_ANGLE / 4);
  }
  
  // Snap to nearest card after scrolling
  const snapAngle = Math.round(rotation.value / CARD_ANGLE) * CARD_ANGLE;
  setTimeout(() => {
    rotation.value = snapAngle;
    const index = (snapAngle / CARD_ANGLE) % providers.length;
    provider.value = providers[Math.abs(index)].id;
  }, 150);
};

onMounted(() => {
  if (carouselTrack.value) {
    carouselTrack.value.addEventListener('wheel', handleWheel, { passive: false });
    
    // Add touch support
    let startX = 0;
    let currentRotation = 0;
    
    carouselTrack.value.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      currentRotation = rotation.value;
    });
    
    carouselTrack.value.addEventListener('touchmove', (e) => {
      const deltaX = e.touches[0].clientX - startX;
      rotation.value = currentRotation + (deltaX / 5);
    });
    
    carouselTrack.value.addEventListener('touchend', () => {
      const snapAngle = Math.round(rotation.value / CARD_ANGLE) * CARD_ANGLE;
      rotation.value = snapAngle;
      const index = (snapAngle / CARD_ANGLE) % providers.length;
      provider.value = providers[Math.abs(index)].id;
    });
  }
});

onUnmounted(() => {
  if (carouselTrack.value) {
    carouselTrack.value.removeEventListener('wheel', handleWheel);
  }
});

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

  // Skip sending prompts if input length is less than 3 or exceeds 100 characters
  if (newMessage.value.trim().length < 6 || newMessage.value.trim().length > 100) {
    currentSuggestion.value = null
    return
  }

  typingTimeout.value = setTimeout(async () => {
    try {
      console.log('Requesting suggestion...')  // Debug log
      const response = await axios.post('http://localhost:5001/api/ollama/chat', {
        messages: [
          {
            role: 'system',
            content: 'without any commentary or answering, you are an autocomplete mechanism that simply completes sentences.'
          },
          {
            role: 'user',
            content: `${newMessage.value.trim()}`
          }
        ],
        model: 'llama3.2:latest'
      })

      console.log('Suggestion response:', response.data)  // Debug log

      if (response.data && response.data.message) {
        currentSuggestion.value = `${newMessage.value.trim()} ${response.data.message}`
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
  
  currentSuggestion.value = null
  
  const userMessage = {
    role: 'user',
    content: newMessage.value.trim()
  }

  // Determine if this is a DALL-E image generation request
  const isDalleRequest = newMessage.value.toLowerCase().includes('/dalle') || 
                        newMessage.value.toLowerCase().includes('/image');

  if (isDalleRequest) {
    messages.value.push(userMessage);
    newMessage.value = '';
    isLoading.value = true;
    
    // Use the specific DALL-E endpoint
    const endpoint = '/api/dalle/generate';
    try {
      const response = await axios.post(`http://localhost:5001${endpoint}`, {
        prompt: newMessage.value.replace(/^\/dalle\s|^\/image\s/i, '').trim()
      });
      
      // Add the generated image to messages
      messages.value.push({
        role: 'assistant',
        content: `![Generated Image](${response.data.url})`,
        model: 'DALL-E'
      });
    } catch (error) {
      console.error('DALL-E error:', error);
      messages.value.push({
        role: 'assistant',
        content: 'Sorry, I encountered an error generating the image. Please try again.',
        model: 'DALL-E'
      });
    } finally {
      isLoading.value = false;
    }
  } else if (selectedImage.value && modelSupportsVision.value) {
    // Handle vision model case...
    const reader = new FileReader();
    reader.onload = async () => {
      const base64Image = reader.result.split(',')[1];
      userMessage.images = [base64Image];
      await sendMessageWithImage(userMessage);
    };
    reader.readAsDataURL(selectedImage.value);
  } else {
    // Regular chat message
    await sendMessageWithImage(userMessage);
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

    let payload;
    if (provider.value === 'ollama') {
      payload = {
        messages: formattedMessages,
        model: selectedModel.value.name  // Just send the model name for Ollama
      }
    } else {
      payload = {
        messages: formattedMessages,
        model: selectedModel.value.name || 'gpt-4-turbo-preview'  // Use the model name, with a fallback
      }
    }
    
    console.log('Sending payload:', payload)
    
    const response = await axios.post(`http://localhost:5001${endpoint}`, payload)

    if (response.data && response.data.message) {
      messages.value.push({
        role: 'assistant',
        content: response.data.message,
        model: selectedModel.value.name
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
  if (!modelInfo) return
  selectedModel.value = {
    name: modelInfo.name || '',
    supportsVision: modelInfo.supportsVision || false
  }
  modelSupportsVision.value = modelInfo.supportsVision || false
  if (!modelSupportsVision.value) {
    removeImage()
  }
}

watch(provider, () => {
  selectedModel.value = {
    name: '',
    supportsVision: false
  }
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

const hasImage = (content) => {
  return content.includes('![Generated Image]') || content.includes('<img')
}

const copyContent = async (message) => {
  try {
    // Remove markdown image syntax if present
    const cleanContent = message.content.replace(/!\[.*?\]\((.*?)\)/g, '$1')
    await navigator.clipboard.writeText(cleanContent)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const handlePaste = async (event) => {
  if (!modelSupportsVision.value) return;
  
  const items = event.clipboardData.items;
  
  for (const item of items) {
    // Handle pasted images
    if (item.type.indexOf('image') !== -1) {
      event.preventDefault();
      const file = item.getAsFile();
      selectedImage.value = file;
      selectedImageUrl.value = URL.createObjectURL(file);
      return;
    }
    
    // Handle pasted text that might be an image URL
    if (item.type === 'text/plain') {
      item.getAsString((text) => {
        if (text.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
          fetch(text)
            .then(res => res.blob())
            .then(blob => {
              const file = new File([blob], "pasted-image.png", { type: blob.type });
              selectedImage.value = file;
              selectedImageUrl.value = URL.createObjectURL(file);
            })
            .catch(err => console.error('Error loading image URL:', err));
        }
      });
    }
  }
};

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const rotateCarousel = (direction) => {
  const delta = direction === 'next' ? -CARD_ANGLE : CARD_ANGLE;
  rotation.value += delta;
  
  // Snap to nearest card after rotation
  const snapAngle = Math.round(rotation.value / CARD_ANGLE) * CARD_ANGLE;
  setTimeout(() => {
    rotation.value = snapAngle;
    const index = Math.abs((snapAngle / CARD_ANGLE) % providers.length);
    provider.value = providers[index].id;
  }, 150);
};

const handleScrollAnimation = () => {
  const scrollbars = document.querySelectorAll('.has-custom-scroll');
  scrollbars.forEach(element => {
    element.classList.add('is-scrolling');
    clearTimeout(element.scrollTimeout);
    element.scrollTimeout = setTimeout(() => {
      element.classList.remove('is-scrolling');
    }, 1000); // Fade out after 1 second of no scrolling
  });
};

onMounted(() => {
  const scrollElements = document.querySelectorAll('.chat-messages, .models-list, pre');
  scrollElements.forEach(element => {
    element.classList.add('has-custom-scroll');
    element.addEventListener('scroll', handleScrollAnimation);
  });
});

onUnmounted(() => {
  const scrollElements = document.querySelectorAll('.has-custom-scroll');
  scrollElements.forEach(element => {
    element.removeEventListener('scroll', handleScrollAnimation);
  });
});
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
  font-family: 'Quicksand', sans-serif;
  overflow: hidden;
}

.sidebar {
  width: 320px;
  height: 100%;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  transition: all 0.3s ease;
  display: flex;
  position: relative;
  padding-right: 12px; /* Add padding to prevent clipping */
  box-sizing: border-box;
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  border-right: none;
}

.sidebar-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  box-sizing: border-box;
  align-items: center;
  text-align: center;
}

.sidebar.collapsed .sidebar-content {
  transform: translateX(-100%);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  max-width: 1200px; /* Increased from 900px */
  margin: 0 auto;
}

.sidebar.collapsed + .chat-container {
  margin-left: auto;
  margin-right: auto;
}

.model-controls {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 16px;
  position: relative;
}

.provider-carousel {
  width: 100%;
  height: 120px;
  perspective: 800px;
  overflow: hidden;
  position: relative;
}

.carousel-viewport {
  width: 90%;
  height: 80%;
  position: relative;
  transform-style: preserve-3d;
}

.carousel-track {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.provider-card {
  position: absolute;
  width: 120px;
  height: 80px;
  left: 50%;
  top: 50%;
  transform-origin: center;
  cursor: pointer;
  transform-style: preserve-3d;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
  margin: -40px -60px;
}

.provider-content {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform-style: preserve-3d;
  transition: all 0.3s ease;
  backface-visibility: hidden;
  opacity: 0.5;
  backdrop-filter: blur(2px);
}

.provider-card:hover .provider-content {
  transform: translateZ(20px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
}

.provider-card.active .provider-content {
  background: var(--bg-secondary);
  border: 2px solid var(--accent-color);
  transform: translateZ(30px);
}

.provider-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.provider-icon svg {
  width: 100%;
  height: 100%;
  color: var(--text-primary);
}

.provider-card.active .provider-icon svg {
  color: var(--accent-color);
}

.provider-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-primary);
  transform: translateZ(8px);
}

/* Touch device support */
@media (hover: none) {
  .provider-carousel {
    touch-action: pan-x;
  }
}

.models-list {
  margin: 0 auto;
  text-align: center;
  max-height: 32px;     /* Much shorter height */
  width: 100%;
  max-width: 200px;     /* Slightly wider */
  overflow-y: auto;
  padding: 1px;         /* Minimal padding */
  border-radius: 6px;
  background: var(--bg-secondary);
}

/* Add styles for the model options */
:deep(.model-option) {
  font-size: 0.7rem;    /* Even smaller font */
  padding: 1px 6px;     /* Minimal vertical padding */
  line-height: 1;       /* Tightest line height */
  white-space: nowrap;  /* Prevent text wrapping */
  height: 16px;         /* Fixed height for options */
  display: flex;
  align-items: center;
}

/* Make scrollbar even more subtle */
.models-list::-webkit-scrollbar {
  width: 2px;
}

.models-list::-webkit-scrollbar-thumb {
  background: var(--accent-color);
  border-radius: 1px;
  opacity: 0.5;
}

.sidebar-footer {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: auto;
  padding-top: 20px;
}

.sidebar-toggle {
  position: absolute;
  right: -32px;
  top: calc(50% - 32px);
  width: 32px;
  height: 64px;
  background: transparent;
  border: none;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  z-index: 10;
  transition: all 0.3s ease;
}

/* Glowing effect when sidebar is collapsed */
.sidebar.collapsed .sidebar-toggle {
  border: 1px solid var(--accent-color);
  border-left: none;
  background: var(--bg-primary);
}

.sidebar-toggle:hover {
  transform: translateX(-1px);
}

.toggle-icon {
  font-size: 20px;
  color: var(--text-primary);
  transition: transform 0.3s ease;
}

.sidebar.collapsed .toggle-icon {
  transform: rotate(180deg);
}

/* Update mobile styles */
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
  }

  .sidebar-toggle {
    width: 24px;
    height: 48px;
    right: -24px;
  }
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
  width: 100%;
  max-width: 232px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-select {
  width: 100%;
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
  text-align: center;
  margin-bottom: 20px;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 100%;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
  opacity: 0;
  transition: all 0.3s ease;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--accent-color);
  border-radius: 3px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* Show scrollbar only when scrolling */
.is-scrolling::-webkit-scrollbar-thumb {
  opacity: 0.8;
}

/* Firefox */
.has-custom-scroll {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.has-custom-scroll.is-scrolling {
  scrollbar-color: var(--accent-color) transparent;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 0.8; }
}

@keyframes fadeOut {
  from { opacity: 0.8; }
  to { opacity: 0; }
}

/* Ensure consistent styling for Firefox */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--accent-color) transparent;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  animation: fadeIn 0.3s ease-out;
  width: 100%;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  width: 100%;
  display: flex;
  gap: 16px;
  max-width: 1000px; /* Increased from 800px */
  margin: 0 auto;
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
  max-width: min(85ch, 800px); /* Increased from 65ch/600px */
  width: 100%;
  position: relative;
  padding: 16px;
  border-radius: 12px;
  background: var(--message-assistant);
  box-shadow: 0 2px 8px var(--shadow-color);
}

/* Specific styling for markdown content */
.markdown-content {
  max-width: 100%;
  overflow-x: auto;
}

/* Image styling */
.markdown-content img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 8px 0;
}

/* DALL-E specific image styling */
.markdown-content img[alt="Generated Image"] {
  max-width: 512px;
  width: 100%;
  height: auto;
}

/* Add responsive adjustments */
@media (max-width: 768px) {
  .message {
    max-width: 90%;
  }
  
  .markdown-content img,
  .markdown-content img[alt="Generated Image"] {
    max-width: 100%;
  }
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
  padding: 12px;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  width: calc(100% - 24px); /* Account for padding */
  box-sizing: border-box;
  margin-left: 12px;
  margin-right: 12px;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
  background: transparent;
  min-width: 0;
}

textarea {
  width: 100%;
  padding: 10px 50px;
  border: 2px solid var(--border-color);
  border-radius: 16px;
  resize: none;
  font-family: 'Quicksand', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1.1rem;
  line-height: 1.6;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 38px;
  max-height: 150px;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
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
    padding: 40px;
    border-right: 3px solid var(--border-color);
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
.sidebar-footer {
  margin-top: auto;
  padding-top: 20px;
}

.clear-chat-btn {
  width: 100%;
  padding: 12px 16px;
  font-size: 0.9rem;
  height: auto;
  min-width: auto;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  opacity: 0.8;
  border-radius: 12px;
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

/* Update mobile styles */
@media (max-width: 768px) {
  .sidebar-footer {
    position: static;
    padding: 30px 1;
  }
}
</style>

<style scoped>
.message-actions {
  position: absolute;
  bottom: -24px;
  left: 24px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(-5px);
  transition: all 0.2s ease;
  z-index: 1;
}

.message:hover .message-actions {
  opacity: 0.7;
  transform: translateY(0);
}

.action-btn {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: auto;  /* Remove minimum width */
  height: auto;     /* Remove fixed height */
  box-shadow: none; /* Remove shadow */
}

.action-btn:hover {
  opacity: 1;
  transform: none;  /* Remove transform */
  background: transparent; /* Stay transparent */
  box-shadow: none;       /* Remove shadow on hover */
}

.copy-icon {
  stroke: var(--text-primary);
  opacity: 0.7;
  width: 16px;
  height: 16px;
}

.action-btn:hover .copy-icon {
  opacity: 1;
}

/* Adjust message spacing */
.message {
  margin-bottom: 32px;
}

/* Dark mode adjustments */
:root {
  --icon-color: #000;
}

.dark-mode {
  --icon-color: #fff;
}

.copy-icon {
  fill: var(--icon-color);
}
</style>

<style>
/* Add new container for bottom buttons */
.carousel-bottom-nav {
  position: relative;
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.carousel-bottom-nav button {
  width: 24px;
  height: 24px;
  background: var(--accent-color);  /* Use accent color by default (light theme) */
  border: 1px solid transparent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;  /* White text/arrows for better contrast */
  font-size: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

/* Dark theme override */
.dark-mode .carousel-bottom-nav button {
  background: rgba(13, 14, 19, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.068);
  color: var(--text-primary);
}

.carousel-bottom-nav button:hover {
  background: var(--accent-color);
  border-color: transparent;
  color: white;
  transform: translateY(-2px);
}
</style>

<style>
/* Update model selector styles */
.models-list {
  max-height: 32px;    /* Even shorter height */
  width: 100%;
  max-width: 200px;     /* Slightly wider */
  margin: 0 auto;
  overflow-y: auto;
  padding: 1px;        /* Minimal padding */
  border-radius: 6px;  /* Smaller border radius */
  background: var(--bg-secondary);
}

/* Add styles for the model selector items */
:deep(.model-option) {
  font-size: 0.7rem;    /* Smaller font */
  padding: 1px 6px;     /* Less vertical padding */
  line-height: 1;       /* Tighter line height */
  white-space: nowrap;  /* Prevent text wrapping */
  height: 16px;         /* Fixed height for options */
  display: flex;
  align-items: center;
}

/* Make scrollbar even more subtle */
.models-list::-webkit-scrollbar {
  width: 2px;          /* Thinner scrollbar */
}

.models-list::-webkit-scrollbar-thumb {
  background: var(--accent-color);
  border-radius: 1px;
  opacity: 0.5;
}
</style>

<style>
/* Target the actual select element */
:deep(select) {
  height: 24px;         /* Short fixed height */
  padding: 2px 6px;     /* Minimal padding */
  font-size: 0.75rem;   /* Small font size */
  line-height: 1;       /* Tight line height */
  border-radius: 6px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  width: 100%;
  max-width: 200px;
}

/* Style the select when opened */
:deep(select:focus) {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

/* Optional: Style for the options within the select */
:deep(option) {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
}
</style>

<style>
/* Add transition to individual sidebar elements */
.chat-header,
.model-controls,
.provider-carousel,
.models-list,
.sidebar-footer {
  opacity: 1;
  transition: opacity 0.2s ease;
  transition-delay: 0.1s;  /* Slight delay for smoother appearance */
}

/* Fade out elements when sidebar is collapsed */
.sidebar.collapsed .chat-header,
.sidebar.collapsed .model-controls,
.sidebar.collapsed .provider-carousel,
.sidebar.collapsed .models-list,
.sidebar.collapsed .sidebar-footer {
  opacity: 0;
  transition-delay: 0s;  /* No delay when hiding */
}

/* Keep the sidebar transition smooth */
.sidebar {
  transition: width 0.3s ease;
}
</style>

<style>
/* Add keyframes for ghostly fade */
@keyframes ghostlyFadeIn {
  0% {
    opacity: 0;
    filter: blur(10px);
    transform: translateY(10px);
  }
  50% {
    opacity: 0.5;
    filter: blur(5px);
  }
  100% {
    opacity: 1;
    filter: blur(0);
    transform: translateY(0);
  }
}

@keyframes ghostlyFadeOut {
  0% {
    opacity: 1;
    filter: blur(0);
    transform: translateX(0);
  }
  50% {
    opacity: 0.6;
    filter: blur(8px);
    transform: translateX(-20px);
  }
  75% {
    opacity: 0.3;
    filter: blur(12px);
    transform: translateX(-30px);
  }
  100% {
    opacity: 0;
    filter: blur(16px);
    transform: translateX(-40px);
  }
}

/* Apply to sidebar elements */
.chat-header,
.model-controls,
.provider-carousel,
.models-list,
.sidebar-footer {
  opacity: 1;
  transition: all 0.5s ease;
  animation: ghostlyFadeIn 0.4s ease forwards;
  transform-origin: left center;
}

/* Ghostly fade out when sidebar collapses */
.sidebar.collapsed .chat-header,
.sidebar.collapsed .model-controls,
.sidebar.collapsed .provider-carousel,
.sidebar.collapsed .models-list,
.sidebar.collapsed .sidebar-footer {
  animation: ghostlyFadeOut 0.6s ease-in-out forwards;
  pointer-events: none;
}

/* Staggered delays for fade out */
.sidebar.collapsed .chat-header { animation-delay: 0s; }
.sidebar.collapsed .model-controls { animation-delay: 0.05s; }
.sidebar.collapsed .provider-carousel { animation-delay: 0.1s; }
.sidebar.collapsed .models-list { animation-delay: 0.15s; }
.sidebar.collapsed .sidebar-footer { animation-delay: 0.2s; }

/* Ensure sidebar transition matches the animation */
.sidebar {
  transition: width 0.6s ease-in-out;
}
</style>

<style>
.markdown-content pre {
  margin: 1em 0;
  padding: 16px; /* Increased padding */
  border-radius: 8px;
  background: var(--code-bg) !important;
  overflow-x: auto;
  position: relative;
}

.markdown-content pre code {
  padding: 0 8px; /* Added horizontal padding for code */
  background: transparent !important; /* Remove background from code inside pre */
  border: none;
  display: block;
  line-height: 1.6;
}

/* For inline code */
.markdown-content p code {
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--code-bg);
}
</style>

<style>
/* Add this to your existing styles */
.sidebar-title {
  position: fixed;
  left: 12px;
  top: 80px;
  transform: rotate(-180deg);
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-secondary);
  opacity: 0;
  transition: opacity 0.5s ease;
  pointer-events: none;
  text-transform: uppercase;
  letter-spacing: 4px;
}

.sidebar.collapsed ~ .chat-container .sidebar-title {
  opacity: 0.15;
  animation: fadeIn 1s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: rotate(-180deg) translateX(20px);
  }
  to {
    opacity: 0.15;
    transform: rotate(-180deg) translateX(0);
  }
}
</style>

<style>
.message-content {
  width: 100%;
  display: flex;
  gap: 16px;
  max-width: 1000px; /* Increased from 800px */
  margin: 0 auto;
}

/* Add these new styles */
.message.user .message-content {
  flex-direction: row-reverse; /* Reverse the order for user messages */
}

.message.user .message-bubble {
  margin-left: 0; /* Remove left margin */
  margin-right: 0; /* Remove right margin */
}

.message.assistant .message-bubble {
  margin-left: 0; /* Remove left margin */
  margin-right: 0; /* Remove right margin */
}

/* Update message actions position for user messages */
.message.user .message-actions {
  left: auto; /* Reset left position */
  right: 24px; /* Position from right instead */
}
</style>

<style scoped>
.button-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.electric-loader {
  animation: pulse 1.5s ease-in-out infinite;
}

.bolt {
  fill: none;
  stroke: white;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 90;
  stroke-dashoffset: 90;
  animation: draw 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(0.9); opacity: 0.7; }
}

@keyframes draw {
  0% { stroke-dashoffset: 90; }
  50% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -90; }
}
</style>