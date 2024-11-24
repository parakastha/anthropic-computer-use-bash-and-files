<template>
  <div class="chat-header">
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<style scoped>
.chat-header {
  padding: 20px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.chat-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: 600;
  text-align: center;
}
</style>
