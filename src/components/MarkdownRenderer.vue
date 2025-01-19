// Inside your component's methods or copy button click handler
async function handleCopy(text) {
  try {
    // Try using the Clipboard API first
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    
    // Fallback: Create a temporary textarea element
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Make the textarea out of viewport
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    
    // Select and copy the text
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
      textArea.remove();
      return true;
    } catch (err) {
      console.error('Failed to copy text:', err);
      textArea.remove();
      return false;
    }
  } catch (err) {
    console.error('Failed to copy text:', err);
    return false;
  }
}

// Usage in your click handler
copyButton.onclick = async () => {
  const textToCopy = /* your text to copy */;
  const success = await handleCopy(textToCopy);
  
  if (success) {
    // Show success message or update UI
    console.log('Text copied successfully');
  } else {
    // Show error message
    console.error('Failed to copy text');
  }
}; 