import axios from 'axios'

const API_URL = 'http://localhost:5001/api'

export function useAIChat() {
  const sendChatMessage = async (messages) => {
    try {
      const response = await axios.post(`${API_URL}/chat`, { messages })
      return response.data
    } catch (error) {
      console.error('Error sending message:', error)
      throw error
    }
  }

  return {
    sendChatMessage
  }
} 