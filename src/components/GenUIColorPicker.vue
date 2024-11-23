<template>
  <div class="color-picker">
    <input type="color" v-model="selectedColor">
    <p>Selected color: {{ selectedColor }}</p>
    <button @click="submit">Submit Color</button>
    <p v-if="submittedColor" class="submitted-response">
      You selected: <span class="color-preview" :style="{ backgroundColor: submittedColor }"></span> {{ submittedColor }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedColor = ref('#000000')
const submittedColor = ref<string | null>(null)
const emit = defineEmits<{
  (e: 'handleSubmit', data: { type: 'colorPicker', color: string }): void
}>()

const submit = () => {
  submittedColor.value = selectedColor.value
  emit('handleSubmit', { type: 'colorPicker', color: selectedColor.value })
}
</script>

<style scoped>
.color-picker {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

input[type="color"] {
  width: 100px;
  height: 50px;
  margin-bottom: 1rem;
}

.color-preview {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  vertical-align: middle;
  margin-right: 5px;
}

.submitted-response {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}
</style>
