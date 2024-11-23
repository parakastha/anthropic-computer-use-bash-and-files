<template>
  <div class="star-rating">
    <div class="stars">
      <span 
        v-for="n in 5" 
        :key="n"
        :class="['star', { active: rating >= n }]"
        @click="setRating(n)"
      >★</span>
    </div>
    <button @click="submit" :disabled="!rating">Submit Rating</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const rating = ref(0)
const emit = defineEmits<{
  (e: 'handleSubmit', data: { type: 'starRating', rating: number }): void
}>()

const setRating = (value: number) => {
  rating.value = value
}

const submit = () => {
  emit('handleSubmit', { type: 'starRating', rating: rating.value })
}
</script>

<style scoped>
.star-rating {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

.stars {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.star {
  font-size: 2rem;
  cursor: pointer;
  color: #ddd;
}

.star.active {
  color: gold;
}
</style>
