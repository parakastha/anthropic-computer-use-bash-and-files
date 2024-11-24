<template>
  <div class="chat-header">
    <div class="header-content">
      <h1>{{ title }}</h1>
    </div>
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
  position: relative;
  z-index: 10;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

h1 {
  margin: 0;
  font-size: 1.75rem;
  background: linear-gradient(135deg, #0056b3, #007AFF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  letter-spacing: -0.5px;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 16px;
  }

  h1 {
    font-size: 1.5rem;
  }
}
</style>
