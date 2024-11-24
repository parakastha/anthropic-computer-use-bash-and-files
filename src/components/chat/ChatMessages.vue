<template>
  <div class="chat-messages" ref="messagesContainer">
    <ChatMessage
      v-for="(message, index) in messages"
      :key="index"
      v-bind="message"
      @handleSubmit="$emit('handleSubmit', $event)"
    />
    <div v-if="isTyping" class="message assistant typing">
      <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import ChatMessage from './ChatMessage.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  error?: string
  componentType?: string
  componentProps?: Record<string, any>
}

const props = defineProps<{
  messages: Message[]
  isTyping: boolean
}>()

defineEmits<{
  handleSubmit: [data: any]
}>()

const messagesContainer = ref<HTMLElement | null>(null)

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Watch messages for changes and scroll to bottom
watch(() => props.messages.length, scrollToBottom)
watch(() => props.isTyping, scrollToBottom)

onMounted(scrollToBottom)
</script>

<style scoped>
.chat-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  padding-bottom: 100px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.typing {
  padding: 12px 16px;
  align-self: flex-start;
  max-width: 85%;
  margin-left: 20px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #007AFF;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
  opacity: 0.7;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { 
    transform: scale(0);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 0.8;
  }
}

@media (max-width: 768px) {
  .chat-messages {
    padding: 16px;
    gap: 12px;
  }

  .typing {
    margin-left: 16px;
    max-width: 90%;
  }
}
</style>
