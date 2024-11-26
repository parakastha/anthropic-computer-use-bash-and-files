<template>
  <div class="chat-input-wrapper">
    <div class="chat-input">
      <textarea 
        ref="textareaRef"
        v-model="inputValue" 
        @keydown.enter.prevent="handleSubmit"
        placeholder="Type your message..."
        rows="1"
        :disabled="isLoading"
      ></textarea>
      <button @click="handleSubmit" :disabled="!inputValue.trim() || isLoading">
        <template v-if="isLoading">
          <span>Thinking</span>
          <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </template>
        <span v-else>Send</span>
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
  background: linear-gradient(to top, rgba(255, 255, 255, 1) 50%, rgba(255, 255, 255, 0.95));
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.chat-input {
  display: flex;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 12px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  transition: all 0.2s ease;
  background: #f8f9fa;
  min-height: 24px;
  max-height: 150px;
}

textarea:focus {
  outline: none;
  border-color: #007AFF;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
  background: white;
}

textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: #f1f3f5;
  border-color: #dee2e6;
}

button {
  padding: 12px 28px;
  background: linear-gradient(135deg, #0056b3, #007AFF);
  color: white;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  min-width: 100px;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(0, 122, 255, 0.25);
  background: linear-gradient(135deg, #0062cc, #0084ff);
}

button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2);
}

button:disabled {
  background: #e9ecef;
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: none;
}

.loading-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.loading-dots span {
  width: 4px;
  height: 4px;
  background: currentColor;
  border-radius: 50%;
  animation: loadingDots 1.4s infinite ease-in-out;
  opacity: 0.7;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes loadingDots {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@media (max-width: 768px) {
  .chat-input-wrapper {
    padding: 16px;
  }
  
  .chat-input {
    padding: 10px;
  }
  
  button {
    padding: 12px 20px;
  }
}
</style>
