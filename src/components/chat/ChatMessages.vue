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

@media (max-width: 768px) {
  .chat-messages {
    padding: 16px;
  }
}
</style>
