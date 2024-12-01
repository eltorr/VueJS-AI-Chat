<template>
  <div class="markdown-content" :class="{ 'is-loading': isLoading }" v-html="renderedContent"></div>
</template>

<script>
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

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
    // Add copy buttons to code blocks after the content is rendered
    this.$nextTick(() => {
      const codeBlocks = this.$el.querySelectorAll('pre code');
      codeBlocks.forEach(block => {
        const pre = block.parentNode;
        const wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';
        
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '📋 Copy';
        copyButton.onclick = () => {
          navigator.clipboard.writeText(block.textContent);
          copyButton.innerHTML = '✅ Copied!';
          setTimeout(() => {
            copyButton.innerHTML = '📋 Copy';
          }, 2000);
        };

        // Move the pre element into the wrapper
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);
        wrapper.appendChild(copyButton);
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
  color: var(--text-primary);
  font-family: var(--font-primary);
  line-height: 1.7;
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

.markdown-content p {
  color: var(--text-primary);
  line-height: 1.6;
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
}

.markdown-content pre {
  background-color: var(--bg-secondary) !important;
  border-radius: 8px;
  padding: 1em;
  overflow: auto;
  margin: 0;
  border: 1px solid var(--border-color);
}

.markdown-content code {
  font-family: var(--font-mono);
  font-size: 90%;
  padding: 0.2em 0.4em;
  margin: 0;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  color: var(--text-primary);
  transition: background-color var(--transition-fast);
}

.markdown-content pre code {
  background-color: transparent;
  padding: 0;
  display: block;
}

.copy-button {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 6px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  opacity: 0;
  font-family: var(--font-primary);
  transition: all var(--transition-bounce);
}

.code-block-wrapper:hover .copy-button {
  opacity: 1;
}

.copy-button:hover {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
  transform: scale(1.05);
}

/* Style for inline code */
.markdown-content p code {
  color: var(--accent-color);
  background-color: var(--bg-secondary);
}

/* Style for blockquotes */
.markdown-content blockquote {
  border-left: 4px solid var(--accent-color);
  margin: 1em 0;
  padding-left: 1em;
  color: var(--text-secondary);
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