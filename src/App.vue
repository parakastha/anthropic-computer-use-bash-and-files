<script setup lang="ts">
import GenUIChat from './components/GenUIChat.vue'
</script>

<template>
  <div class="app-container">
    <header>
      <h1>Xuno Chat</h1>
    </header>
    <main>
      <GenUIChat />
    </main>
  </div>
</template>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

#app {
  height: 100vh;
  background: #f8f9fa;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  margin: 0;
  padding: 0;
}

header {
  background: #fff;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

header h1 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
  overflow-y: auto;
  height: calc(100vh - 60px); /* Adjust based on header height */
}
</style>
