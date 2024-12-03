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
  --bg-primary: #16171f;      /* Darker base background */
  --bg-secondary: #1f2335;    /* Darker secondary background */
  --text-primary: #a9b1d6;    /* Slightly darker text */
  --text-secondary: #565f89;  /* Darker secondary text */
  --accent-color: #6889e0;    /* Darker accent blue */
  --message-user: #324179;    /* Darker user message gradient start */
  --message-assistant: #1f2335;  /* Darker message background */
  --border-color: #222738;    /* Darker border color */
  --table-border: #222738;    /* Match border color */
  --code-bg: #1a1b26;         /* Darker code background */
  --shadow-color: rgba(0, 0, 0, 0.6);  /* Stronger shadow */
}

.dark-mode .chat-input {
  background: var(--bg-secondary);
  box-shadow: 0 8px 32px var(--shadow-color);
}

.dark-mode .message-bubble {
  box-shadow: 0 2px 8px var(--shadow-color);
}

.dark-mode .message.user .message-bubble {
  background: linear-gradient(135deg, var(--message-user), #1e3a8a);
}

.dark-mode .message.assistant .message-bubble {
  background: var(--message-assistant);
  border: 1px solid var(--border-color);
}

.dark-mode button {
  background: var(--bg-secondary);
}

.dark-mode button:hover:not(:disabled) {
  background: var(--accent-color);
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.15);
}

.dark-mode button:disabled {
  background: var(--bg-secondary);
  opacity: 0.5;
}

.dark-mode textarea {
  background: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.dark-mode textarea:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.dark-mode .message-avatar {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.dark-mode .markdown-content code {
  background: var(--code-bg);
  border: 1px solid var(--border-color);
}

.dark-mode .markdown-content pre {
  background: var(--code-bg) !important;
  border: 1px solid var(--border-color);
}

.dark-mode .markdown-content blockquote {
  background: var(--bg-secondary);
  border-left: 4px solid var(--accent-color);
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

.models-list {
  max-height: 60px;     /* Even shorter height */
  width: 100%;
  max-width: 180px;     /* Wider width */
  margin: 0 auto;
  overflow-y: auto;
  padding: 2px;
  border-radius: 8px;
  background: var(--bg-secondary);
  font-size: 0.8rem;
}

.dark-mode .models-list {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
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

/* Add styles for the model options */
:deep(.model-option) {
  font-size: 0.75rem;   /* Smaller font */
  padding: 2px 6px;     /* Less vertical padding */
  line-height: 1;       /* Tighter line height */
  white-space: nowrap;  /* Prevent text wrapping */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.message {
  width: 100%;
  max-width: 800px;
  margin-bottom: 32px;
  padding: 0 20px;
}

.message-bubble {
  max-width: min(65ch, 600px);
  width: 100%;
  position: relative;
  padding: 16px;
  border-radius: 12px;
  background: var(--message-assistant);
  box-shadow: 0 2px 8px var(--shadow-color);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--message-user), var(--accent-color));
  color: white;
}

/* Ensure mobile responsiveness */
@media (max-width: 768px) {
  .message {
    max-width: 100%;
    padding: 0 10px;
  }
  
  .message-bubble {
    max-width: 100%;
  }
}
</style>