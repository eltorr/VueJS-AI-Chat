<template>
  <div class="dalle-container">
    <div class="controls">
      <textarea 
        v-model="imagePrompt" 
        placeholder="Describe the image you want to generate..."
        class="prompt-input"
        @input="handleInput"
      ></textarea>
      <button 
        @click="generateImage" 
        :disabled="isLoading || !imagePrompt.trim()"
      >
        <span class="button-content">
          <span v-if="isLoading" class="loader"></span>
          <span v-else>Generate Image</span>
        </span>
      </button>
    </div>

    <div v-if="generatedImage" class="image-display">
      <img :src="generatedImage" alt="Generated image" />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'DallEGenerator',
  setup() {
    const imagePrompt = ref('')
    const isLoading = ref(false)
    const generatedImage = ref(null)

    const handleInput = (e) => {
      const textarea = e.target
      textarea.style.height = 'auto'
      textarea.style.height = textarea.scrollHeight + 'px'
    }

    const generateImage = async () => {
      if (!imagePrompt.value.trim() || isLoading.value) return

      isLoading.value = true
      try {
        const response = await axios.post('http://localhost:5001/api/dalle/generate', {
          prompt: imagePrompt.value
        })

        if (response.data && response.data.url) {
          generatedImage.value = response.data.url
        }
      } catch (error) {
        console.error('Image generation error:', error)
        alert('Error generating image. Please try again.')
      } finally {
        isLoading.value = false
      }
    }

    return {
      imagePrompt,
      isLoading,
      generatedImage,
      handleInput,
      generateImage
    }
  }
}
</script>

<style scoped>
.dalle-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.controls {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.prompt-input {
  flex: 1;
  min-height: 48px;
  padding: 12px 20px;
  border: 2px solid var(--border-color);
  border-radius: 16px;
  resize: none;
  font-family: 'Quicksand', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1.1rem;
  line-height: 1.6;
}

button {
  height: 48px;
  padding: 0 24px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 600;
  font-family: 'Quicksand', sans-serif;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

button:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
}

.image-display {
  margin-top: 20px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-display img {
  width: 100%;
  height: auto;
  display: block;
}

.loader {
  width: 20px;
  height: 20px;
  border: 3px solid #ffffff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 