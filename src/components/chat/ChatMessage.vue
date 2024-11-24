<template>
  <div :class="['message', role]">
    <div class="message-content">
      <component 
        v-if="role === 'assistant' && componentType"
        :is="resolveComponent(componentType)"
        v-bind="componentProps"
        @handleSubmit="$emit('handleSubmit', $event)"
      />
      <div v-else class="message-text">{{ content }}</div>
      <div class="message-timestamp">{{ formatTimestamp(timestamp) }}</div>
      <div v-if="error" class="message-error">Error: {{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import GenUIText from '../GenUIText.vue'
import GenUIStarRating from '../GenUIStarRating.vue'
import GenUIColorPicker from '../GenUIColorPicker.vue'
import GenUIContactForm from '../GenUIContactForm.vue'

const props = defineProps<{
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  error?: string
  componentType?: string
  componentProps?: Record<string, any>
}>()

defineEmits<{
  handleSubmit: [data: any]
}>()

const resolveComponent = (type: string) => {
  const components = {
    text: markRaw(GenUIText),
    starRating: markRaw(GenUIStarRating),
    colorPicker: markRaw(GenUIColorPicker),
    contactForm: markRaw(GenUIContactForm),
    errorMessage: markRaw(GenUIText)
  }
  return components[type as keyof typeof components] || markRaw(GenUIText)
}

const formatTimestamp = (date: Date): string => {
  return new Intl.DateTimeFormat('en', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true
  }).format(date)
}
</script>

<style scoped>
.message {
  width: 100%;
  word-wrap: break-word;
  max-width: 80%;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 16px;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.message-text {
  font-size: 1rem;
  line-height: 1.5;
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
}

.message.assistant {
  align-self: flex-start;
}

.user .message-content {
  background: linear-gradient(135deg, #0056b3, #007AFF);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.15);
}

.assistant .message-content {
  background: #f8f9fa;
  color: #2c3e50;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .message {
    max-width: 85%;
  }
}
</style>
