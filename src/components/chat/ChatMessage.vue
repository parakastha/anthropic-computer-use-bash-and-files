<template>
  <div :class="['message', role]">
    <div class="message-content">
      <component 
        v-if="role === 'assistant' && componentType"
        :is="resolveComponent(componentType)"
        v-bind="{ text: content, ...componentProps }"
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
import GenUIFAQ from '../GenUIFAQ.vue'

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
    faq: markRaw(GenUIFAQ),
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
  max-width: 85%;
  margin: 8px auto;
  word-wrap: break-word;
}

.message.user {
  margin-left: auto;
}

.message.assistant {
  margin-right: auto;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  text-align: left;
  max-width: 100%;
  width: 100%;
}

.user .message-content {
  background: linear-gradient(135deg, #0056b3, #007AFF);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 122, 255, 0.15);
  margin-left: auto;
}

.assistant .message-content {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border: 1px solid rgba(0, 0, 0, 0.05);
  margin-right: auto;
  width: 100%;
}

.message-text {
  font-size: 1rem;
  line-height: 1.6;
  white-space: pre-wrap;
  color: #2c3e50;
  font-weight: 400;
  width: 100%;
}

.message-timestamp {
  font-size: 0.75rem;
  opacity: 0.7;
  align-self: flex-end;
}

.message-error {
  color: #dc3545;
  font-size: 0.875rem;
  padding: 8px;
  border-radius: 8px;
  background: rgba(220, 53, 69, 0.1);
}

@media (max-width: 768px) {
  .message {
    max-width: 90%;
  }
}
</style>
