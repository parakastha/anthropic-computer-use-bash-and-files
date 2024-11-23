<template>
  <div class="color-picker">
    <input type="color" v-model="selectedColor">
    <p>Selected color: {{ selectedColor }}</p>
    <button @click="submit">Submit Color</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedColor = ref('#000000')
const emit = defineEmits<{
  (e: 'handleSubmit', data: { type: 'colorPicker', color: string }): void
}>()

const submit = () => {
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
</style>
