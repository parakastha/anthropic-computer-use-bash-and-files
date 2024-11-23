<template>
  <div class="text-component">
    <p>{{ textResponse }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  textResponse: string
}>()
</script>

<style scoped>
.text-component {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}
</style>
