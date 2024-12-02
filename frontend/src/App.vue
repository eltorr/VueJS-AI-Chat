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
  --message-assistant: #f0f4f8;
  --border-color: #e9ecef;
  --table-border: #dee2e6;
  --code-bg: #f8f9fa;
  --shadow-color: rgba(0, 0, 0, 0.1);
  
  /* Typography */
  --font-primary: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
  --font-handwriting: 'Caveat', 'Kalam', cursive;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Animation constants */
  --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-bounce: 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.dark-mode {
  --bg-primary: #000000;
  --bg-secondary: #111111;
  --text-primary: #e0e0e0;
  --text-secondary: #888888;
  --accent-color: #2563eb;
  --message-user: #1e40af;
  --message-assistant: #171717;
  --border-color: #222222;
  --table-border: #333333;
  --code-bg: #0a0a0a;
  --shadow-color: rgba(0, 0, 0, 0.5);
}

.dark-mode .chat-input {
  background: #111111;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.dark-mode .message-bubble {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-mode .message.user .message-bubble {
  background: linear-gradient(135deg, #1e40af, #1e3a8a);
}

.dark-mode .message.assistant .message-bubble {
  background: #171717;
  border: 1px solid #222222;
}

.dark-mode button {
  background: #2563eb;
}

.dark-mode button:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.15);
}

.dark-mode button:disabled {
  background: #333333;
  opacity: 0.5;
}

.dark-mode textarea {
  background: #171717;
  border-color: #222222;
  color: #e0e0e0;
}

.dark-mode textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.dark-mode .message-avatar {
  background: #171717;
  border: 1px solid #222222;
}

.dark-mode .markdown-content code {
  background: #0a0a0a;
  border: 1px solid #222222;
}

.dark-mode .markdown-content pre {
  background: #0a0a0a !important;
  border: 1px solid #222222;
}

.dark-mode .markdown-content blockquote {
  background: #111111;
  border-left: 4px solid #2563eb;
}

/* Add this in the head section */
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Kalam:wght@300;400;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

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