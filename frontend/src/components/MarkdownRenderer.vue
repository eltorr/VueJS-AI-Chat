<template>
  <div class="markdown-content" :class="{ 'is-loading': isLoading }" v-html="renderedContent"></div>
</template>

<script>
import { marked } from 'marked';
import hljs from 'highlight.js';
// Import a theme - you can choose from many available themes
import 'highlight.js/styles/tokyo-night-dark.css';  // Dark theme that works well with our color scheme
// Optional: Import additional languages if needed
import 'highlight.js/lib/languages/python';
import 'highlight.js/lib/languages/javascript';
import 'highlight.js/lib/languages/bash';
import 'highlight.js/lib/languages/json';
import 'highlight.js/lib/languages/xml';
import 'highlight.js/lib/languages/css';

export default {
  name: 'MarkdownRenderer',
  props: {
    content: {
      type: String,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    // Highlight all code blocks after the content is rendered
    this.$nextTick(() => {
      const codeBlocks = this.$el.querySelectorAll('pre code');
      codeBlocks.forEach(block => {
        hljs.highlightElement(block);
        
        // Add language label if available
        const language = block.className.replace('language-', '');
        if (language && language !== 'undefined') {
          const pre = block.parentNode;
          const wrapper = document.createElement('div');
          wrapper.className = 'code-block-wrapper';
          
          const languageLabel = document.createElement('div');
          languageLabel.className = 'code-language-label';
          languageLabel.textContent = language;
          
          const copyButton = document.createElement('button');
          copyButton.className = 'copy-button';
          copyButton.innerHTML = ' Copy';
          copyButton.onclick = () => {
            navigator.clipboard.writeText(block.textContent);
            copyButton.innerHTML = '✅ Copied!';
            setTimeout(() => {
              copyButton.innerHTML = '📋 Copy';
            }, 2000);
          };

          const controls = document.createElement('div');
          controls.className = 'code-controls';
          controls.appendChild(languageLabel);
          controls.appendChild(copyButton);

          pre.parentNode.insertBefore(wrapper, pre);
          wrapper.appendChild(controls);
          wrapper.appendChild(pre);
        }
      });
    });
  },
  computed: {
    renderedContent() {
      marked.setOptions({
        highlight: function(code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
          }
          return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
      });
      return marked(this.content);
    }
  }
}
</script>

<style>
.markdown-content {
  text-align: left;
  line-height: 1.7;
}

.markdown-content p {
  margin: 0.5em 0;
  font-family: inherit !important;
}

.markdown-content blockquote {
  font-family: 'Caveat', cursive !important;
  font-size: 1.4em;
  line-height: 1.6;
  border-left: 4px solid var(--accent-color);
  margin: 1.5em 0;
  padding: 1em 1.5em;
  background-color: var(--bg-secondary);
  border-radius: 0 8px 8px 0;
  font-weight: 500;
}

.markdown-content code {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9em;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  background-color: var(--code-bg);
  color: var(--accent-color);
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  color: var(--text-primary);
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-content a {
  color: var(--accent-color);
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.code-block-wrapper {
  position: relative;
  margin: 1.5em 0;
  background: var(--code-bg);
  border-radius: 8px;
  overflow: hidden;
}

.code-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--border-color);
}

.code-language-label {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.copy-button {
  font-family: var(--font-primary);
  font-size: 0.9rem;
  padding: 4px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-button:hover {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.markdown-content pre {
  margin: 0;
  padding: 16px;
  background: var(--code-bg) !important;
  overflow-x: auto;
}

.markdown-content pre code {
  padding: 0;
  background: transparent;
  border: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Customize scrollbar for code blocks */
.markdown-content pre::-webkit-scrollbar {
  height: 8px;
}

.markdown-content pre::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

.markdown-content pre::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.markdown-content pre::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

/* Dark mode specific styles */
.dark-mode .code-controls {
  background: rgba(0, 0, 0, 0.4);
}

.dark-mode .copy-button {
  color: var(--text-secondary);
  border-color: var(--border-color);
}

.dark-mode .copy-button:hover {
  background: var(--accent-color);
  color: white;
}

/* Style for inline code */
.markdown-content p code {
  color: var(--accent-color);
  background-color: var(--bg-secondary);
}

/* Style for lists */
.markdown-content ul,
.markdown-content ol {
  color: var(--text-primary);
  padding-left: 1.5em;
}

/* Style for tables */
.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid var(--border-color);
  padding: 8px;
  text-align: left;
}

.markdown-content th {
  background-color: var(--bg-secondary);
}

/* Style for horizontal rules */
.markdown-content hr {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 2em 0;
}

@keyframes loadingLine {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.markdown-content.is-loading {
  position: relative;
}

.markdown-content.is-loading::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%,
    var(--accent-color) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: loadingLine 2s infinite linear;
}
</style>