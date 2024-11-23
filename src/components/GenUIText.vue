<template>
  <div class="text-component">
    <p>{{ textResponse }}</p>
    <button @click="submit">Submit</button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  textResponse: string
}>()

const emit = defineEmits<{
  (e: 'handleSubmit', data: { type: 'text', response: string }): void
}>()

const submit = () => {
  emit('handleSubmit', { type: 'text', response: props.textResponse })
}
</script>

<style scoped>
.text-component {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}
</style>
