<template>
  <div class="model-selector">
    <select v-model="selectedModel" @change="handleModelChange">
      <option value="" disabled>Select a model</option>
      <option v-for="model in filteredModels" 
              :key="model.name || model" 
              :value="model.name || model">
        {{ model.name || model }}
      </option>
    </select>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ModelSelector',
  props: {
    provider: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      models: [],
      selectedModel: '',
      isLoading: false,
      error: null
    }
  },
  computed: {
    filteredModels() {
      return this.models
    },
    supportsVision() {
      if (this.provider === 'ollama') {
        return this.selectedModel?.includes('vision')
      }
      return false
    }
  },
  watch: {
    provider: {
      immediate: true,
      handler: 'fetchModels'
    }
  },
  methods: {
    async fetchModels() {
      this.isLoading = true
      this.error = null
      try {
        const endpoint = this.provider === 'ollama' 
          ? '/api/ollama/models' 
          : '/api/openai/models'
        const response = await axios.get(`http://localhost:5001${endpoint}`)
        
        if (this.provider === 'ollama') {
          this.models = response.data.models.map(model => model.name || model)
        } else {
          this.models = response.data.models.map(m => m.name)
        }

        if (this.models.length > 0) {
          this.selectedModel = this.models[0]
          this.handleModelChange()
        }
      } catch (error) {
        console.error('Error fetching models:', error)
        this.error = 'Failed to load models: ' + error.message
      } finally {
        this.isLoading = false
      }
    },
    handleModelChange() {
      this.$emit('model-selected', {
        name: this.selectedModel,
        supportsVision: this.supportsVision
      })
    }
  }
}
</script>

<style scoped>
.model-selector {
  width: 100%;
  margin: 0;
}

select {
  width: 100%;
  height: 24px;
  padding: 2px 20px 2px 6px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.75rem;
  font-weight: normal;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 4px center;
  background-size: 12px;
}

select:focus {
  outline: none;
  border-color: var(--accent-color);
}

select option {
  padding: 2px 6px;
  font-size: 0.75rem;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* Remove fluid typography */
@media screen and (min-width: 320px) {
  select {
    font-size: 0.75rem;
    padding: 2px 20px 2px 6px;
  }
}

/* Remove mobile adjustments or keep them minimal */
@media (max-width: 768px) {
  select {
    padding: 2px 20px 2px 6px;
  }
}
</style> 