# Create new file
<template>
  <div class="faq-component">
    <div class="accordion">
      <div v-for="(item, index) in parseFAQItems(text)" :key="index" class="accordion-item">
        <div 
          class="accordion-header"
          :class="{ 'active': activeItem === index }"
          @click="toggleItem(index)"
        >
          <h3>{{ item.question }}</h3>
          <span class="accordion-icon">{{ activeItem === index ? '−' : '+' }}</span>
        </div>
        <div 
          class="accordion-content"
          :class="{ 'active': activeItem === index }"
        >
          <p>{{ item.answer }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  text: string
}>()

const activeItem = ref<number | null>(null)

const parseFAQItems = (text: string) => {
  const items = []
  const lines = text.split('\n')
  let currentQuestion = ''
  let currentAnswer = ''

  for (const line of lines) {
    if (line.match(/^\d+\./) || line.includes('Q:')) {
      if (currentQuestion) {
        items.push({ question: currentQuestion.trim(), answer: currentAnswer.trim() })
        currentAnswer = ''
      }
      currentQuestion = line.replace(/^\d+\.\s*/, '').replace('Q:', '').trim()
    } else if (line.includes('A:')) {
      currentAnswer = line.replace('A:', '').trim()
    } else if (line.trim() && currentQuestion) {
      if (currentAnswer) {
        currentAnswer += ' ' + line.trim()
      } else {
        currentQuestion += ' ' + line.trim()
      }
    }
  }

  if (currentQuestion) {
    items.push({ question: currentQuestion.trim(), answer: currentAnswer.trim() })
  }

  return items
}

const toggleItem = (index: number) => {
  activeItem.value = activeItem.value === index ? null : index
}
</script>

<style scoped>
.faq-component {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.accordion {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.accordion-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.accordion-item:last-child {
  border-bottom: none;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.accordion-header:hover {
  background: rgba(0, 122, 255, 0.05);
}

.accordion-header.active {
  background: rgba(0, 122, 255, 0.1);
}

.accordion-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.5;
}

.accordion-icon {
  font-size: 1.25rem;
  color: #007AFF;
  transition: transform 0.2s ease;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 1rem;
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease-in-out;
  background: white;
}

.accordion-content.active {
  max-height: 500px;
  padding: 1.5rem;
  background: rgba(0, 122, 255, 0.02);
}

.accordion-content p {
  margin: 0;
  line-height: 1.6;
  color: #4a5568;
  font-size: 0.95rem;
}
</style> 