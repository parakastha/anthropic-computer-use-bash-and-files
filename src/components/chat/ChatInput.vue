<template>
  <div class="chat-input-wrapper">
    <div class="chat-input">
      <textarea 
        ref="textareaRef"
        v-model="inputValue" 
        @keydown.enter.prevent="handleSubmit"
        placeholder="Type your message..."
        rows="3"
        :disabled="isLoading"
      ></textarea>
      <button @click="handleSubmit" :disabled="!inputValue.trim() || isLoading">
        <span v-if="!isLoading">Send</span>
        <span v-else>Sending...</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  isLoading: boolean
}>()

const emit = defineEmits<{
  submit: [message: string]
}>()

const inputValue = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// Watch input and capitalize first letter while typing
watch(inputValue, (newValue) => {
  if (newValue && newValue.length > 0) {
    const shouldCapitalize = newValue.length === 1 || (newValue.length > 1 && newValue[newValue.length - 2] === '\n');
    if (shouldCapitalize) {
      inputValue.value = newValue.charAt(newValue.length - 1).toUpperCase() + newValue.slice(newValue.length);
    }
  }
})

const handleSubmit = () => {
  const trimmedInput = inputValue.value.trim()
  if (!trimmedInput || props.isLoading) return
  
  const capitalizedInput = trimmedInput.charAt(0).toUpperCase() + trimmedInput.slice(1)
  emit('submit', capitalizedInput)
  inputValue.value = ''
  
  nextTick(() => {
    textareaRef.value?.focus()
  })
}
</script>

<style scoped>
.chat-input-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px;
  background: linear-gradient(to top, white, rgba(255, 255, 255, 0.9));
  backdrop-filter: blur(10px);
}

.chat-input {
  display: flex;
  gap: 12px;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  resize: none;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.5;
  transition: all 0.2s ease;
  background: white;
}

textarea:focus {
  outline: none;
  border-color: #007AFF;
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
}

textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #0056b3, #007AFF);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 100px;
  box-shadow: 0 2px 4px rgba(0, 122, 255, 0.2);
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 122, 255, 0.3);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:disabled {
  background: #e9ecef;
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: none;
}

@media (max-width: 768px) {
  .chat-input-wrapper {
    padding: 16px;
  }
}
</style>
