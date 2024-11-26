<template>
  <div class="page-container">
    <div class="chat-container">
      <ChatHeader title="Xuno Chat" />
      <div class="chat-content">
        <ChatMessages 
          :messages="messages" 
          :isTyping="isTyping"
          @handleSubmit="handleDynamicSubmit"
        />
        <ChatInput 
          :isLoading="isLoading"
          @submit="sendMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ChatHeader from './chat/ChatHeader.vue'
import ChatMessages from './chat/ChatMessages.vue'
import ChatInput from './chat/ChatInput.vue'
import type { ChatMessage } from './chat/types'

const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
const isTyping = ref(false)
const sessionId = ref<string | null>(null)

const generateId = () => Math.random().toString(36).substring(2, 15)

const simulateTyping = () => {
  isTyping.value = true
  setTimeout(() => {
    isTyping.value = false
  }, 1000)
}

const sendMessage = async (message: string) => {
  if (isLoading.value) return
  
  isLoading.value = true
  isTyping.value = true
  
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date(),
    id: generateId(),
    createdAt: Date.now()
  })

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        message,
        sessionId: sessionId.value  
      })
    })

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const data = await response.json()
    
    // Add a small delay to show typing animation
    await new Promise(resolve => setTimeout(resolve, 500))
    
    if (!sessionId.value) {
      sessionId.value = data.sessionId
    }
    
    messages.value.push({
      role: 'assistant',
      content: data.response,
      timestamp: new Date(),
      id: generateId(),
      createdAt: Date.now(),
      componentType: data.uiComponent?.type || 'text',
      componentProps: { 
        textResponse: data.response,
        ...(data.uiComponent?.type === 'contactForm' && {
          onSubmit: (formData: any) => {
            console.log('Contact form submitted:', formData)
            handleDynamicSubmit(formData)
          }
        })
      }
    })

    // Add a small delay before removing typing indicator
    await new Promise(resolve => setTimeout(resolve, 300))
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, there was an error processing your request.',
      timestamp: new Date(),
      id: generateId(),
      createdAt: Date.now(),
      error: error instanceof Error ? error.message : 'Unknown error',
      componentType: 'errorMessage',
      componentProps: { 
        textResponse: 'Sorry, there was an error processing your request.' 
      }
    })
  } finally {
    isTyping.value = false
    isLoading.value = false
  }
}

const handleDynamicSubmit = (data: any) => {
  console.log('Component submitted:', data)
  if (data.type === 'contactForm') {
    messages.value.push({
      role: 'assistant',
      content: `Thank you for your submission! I've received your contact information:\nName: ${data.formData.name}\nEmail: ${data.formData.email}\nMessage: ${data.formData.message}`,
      timestamp: new Date(),
      id: generateId(),
      createdAt: Date.now(),
      componentType: 'text',
      componentProps: { 
        textResponse: `Thank you for your submission! I've received your contact information:\nName: ${data.formData.name}\nEmail: ${data.formData.email}\nMessage: ${data.formData.message}`
      }
    })
  }
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: 'Hi! How can I help you today?',
    timestamp: new Date(),
    id: generateId(),
    createdAt: Date.now(),
    componentType: 'text',
    componentProps: { textResponse: 'Hi! How can I help you today?' }
  })
})
</script>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #f0f2f5 0%, #e9ecef 100%);
  padding: 20px;
  margin: 0;
  box-sizing: border-box;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.chat-container {
  width: 100%;
  max-width: 1000px;
  height: 90vh;
  background: white;
  border-radius: 24px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  margin: 0 auto;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  height: calc(100% - 70px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(248, 249, 250, 0.5) 100%);
}

@media (max-width: 768px) {
  .page-container {
    padding: 0;
    margin: 0;
  }

  .chat-container {
    height: 100vh;
    border-radius: 0;
    margin: 0;
    box-shadow: none;
  }
}
</style>
