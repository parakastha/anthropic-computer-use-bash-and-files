<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <div class="message-content">
          <component 
            v-if="message.componentType"
            :is="resolveComponent(message.componentType)"
            v-bind="message.componentProps"
            @handleSubmit="handleDynamicSubmit"
          />
          <div v-else class="message-text">{{ message.content }}</div>
          <div class="message-timestamp">{{ formatTimestamp(message.timestamp) }}</div>
          <div v-if="message.error" class="message-error">Error: {{ message.error }}</div>
        </div>
      </div>
      <div v-if="isTyping" class="message assistant typing">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <textarea 
        v-model="userInput" 
        @keydown.enter.prevent="sendMessage"
        placeholder="Type your message..."
        rows="3"
        :disabled="isLoading"
      ></textarea>
      <button @click="sendMessage" :disabled="!userInput.trim() || isLoading">
        <span v-if="!isLoading">Send</span>
        <span v-else>Sending...</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, markRaw } from 'vue'
import GenUIText from './GenUIText.vue'
import GenUIStarRating from './GenUIStarRating.vue'
import GenUIColorPicker from './GenUIColorPicker.vue'
import GenUIContactForm from './GenUIContactForm.vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  error?: string
  id: string
  componentType?: string
  componentProps?: Record<string, any>
  submitResponse?: Record<string, any>
  createdAt: number
}

// Add component resolution function
const resolveComponent = (type: string) => {
  const components = {
    text: markRaw(GenUIText),
    starRating: markRaw(GenUIStarRating),
    colorPicker: markRaw(GenUIColorPicker),
    contactForm: markRaw(GenUIContactForm),
    userMessage: markRaw(GenUIText),
    textMessage: markRaw(GenUIText),
    errorMessage: markRaw(GenUIText)
  }
  return components[type as keyof typeof components] || markRaw(GenUIText)
}

// Add submit handler
const handleDynamicSubmit = (data: any) => {
  console.log('Component submitted:', data)
  // Handle the submission based on the component type
  // You can add specific handling logic here
}

const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const isLoading = ref(false)
const isTyping = ref(false)
const sessionId = ref<string | null>(null)

const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2)
}

const formatTimestamp = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(date)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const simulateTyping = async () => {
  isTyping.value = true
  await scrollToBottom()
}

const sendMessage = async () => {
  const trimmedInput = userInput.value.trim()
  if (!trimmedInput || isLoading.value) return

  isLoading.value = true
  
  // Add user message
  messages.value.push({
    role: 'user',
    content: trimmedInput,
    timestamp: new Date(),
    id: generateId(),
    createdAt: Date.now(),
    componentType: 'userMessage',
    componentProps: { text: trimmedInput }
  })
  userInput.value = ''
  await scrollToBottom()

  try {
    await simulateTyping()
    
    const response = await fetch('http://localhost:3000/tool', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        message: trimmedInput,
        sessionId: sessionId.value  
      })
    })

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const data = await response.json()
    isTyping.value = false
    
    if (data.sessionId) {
      sessionId.value = data.sessionId
    }
    
    messages.value.push({
      role: 'assistant',
      content: JSON.stringify(data, null, 2),
      timestamp: new Date(),
      id: generateId(),
      createdAt: Date.now(),
      componentType: data.uiComponent?.type || 'textMessage',
      componentProps: { textResponse: data.uiComponent?.text || data.response },
      submitResponse: data
    })
  } catch (error) {
    console.error('Error:', error)
    isTyping.value = false
    
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error processing your request.',
      timestamp: new Date(),
      error: error instanceof Error ? error.message : 'Unknown error',
      id: generateId(),
      createdAt: Date.now(),
      componentType: 'errorMessage',
      componentProps: { 
        text: 'Sorry, I encountered an error processing your request.',
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: 'Hello! How can I help you today?',
    timestamp: new Date(),
    id: generateId(),
    createdAt: Date.now(),
    componentType: 'textMessage',
    componentProps: { textResponse: 'Hello! How can I help you today?' }
  })
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  border-radius: 8px;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  font-size: 1rem;
}

.message-timestamp {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
}

.message-error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 4px;
}

.message.user {
  align-self: flex-end;
  background: #007AFF;
  color: white;
}

.message.assistant {
  align-self: flex-start;
  background: white;
  color: #333;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.typing {
  padding: 12px 16px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #007AFF;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input {
  display: flex;
  gap: 10px;
}

textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: inherit;
}

textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

button {
  padding: 12px 24px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  min-width: 100px;
}

button:hover:not(:disabled) {
  background: #0056b3;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
