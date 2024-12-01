<template>
  <div id="app" :class="{ 'dark-mode': isDarkMode }">
    <div class="theme-toggle" @click="toggleDarkMode">
      <span class="theme-icon">{{ isDarkMode ? '🌙' : '☀️' }}</span>
    </div>
    <ChatInterface />
  </div>
</template>

<script>
import { ref } from 'vue'
import ChatInterface from './components/ChatInterface.vue'

export default {
  name: 'App',
  components: {
    ChatInterface
  },
  setup() {
    const isDarkMode = ref(false)
    
    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      localStorage.setItem('darkMode', isDarkMode.value)
    }

    // Initialize dark mode from localStorage
    isDarkMode.value = localStorage.getItem('darkMode') === 'true'

    return {
      isDarkMode,
      toggleDarkMode
    }
  }
}
</script>

<style>
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --text-primary: #2c3e50;
  --text-secondary: #6c757d;
  --accent-color: #3498db;
  --message-user: #3498db;
  --message-assistant: #f8f9fa;
  --border-color: #e9ecef;
}

.dark-mode {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --accent-color: #60a5fa;
  --message-user: #3b82f6;
  --message-assistant: #374151;
  --border-color: #404040;

  /* Typography */
  --font-primary: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
  
  /* Animation constants */
  --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-bounce: 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}  

/* Add these new styles */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden; /* Prevent body scrolling */
  background-color: var(--bg-primary);
  transition: background-color 0.3s ease;
}

#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
  overflow: hidden; /* Prevent app scrolling */
}

#app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  margin: 0;
  padding: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  cursor: pointer;
  background: var(--bg-secondary);
  padding: 10px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

.theme-icon {
  font-size: 1.5rem;
}
</style>