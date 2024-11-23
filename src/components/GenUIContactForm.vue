<template>
  <form class="contact-form" @submit.prevent="submit">
    <div class="form-group">
      <label for="name">Name:</label>
      <input type="text" id="name" v-model="formData.name" required>
    </div>
    <div class="form-group">
      <label for="email">Email:</label>
      <input type="email" id="email" v-model="formData.email" required>
    </div>
    <div class="form-group">
      <label for="message">Message:</label>
      <textarea id="message" v-model="formData.message" required></textarea>
    </div>
    <button type="submit">Submit</button>
  </form>
  <div v-if="submitted" class="submitted-response">
    <h3>Submitted Information:</h3>
    <p><strong>Name:</strong> {{ submittedData?.name }}</p>
    <p><strong>Email:</strong> {{ submittedData?.email }}</p>
    <p><strong>Message:</strong> {{ submittedData?.message }}</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const formData = reactive({
  name: '',
  email: '',
  message: ''
})

const submitted = ref(false)
const submittedData = ref<typeof formData | null>(null)

const emit = defineEmits<{
  (e: 'handleSubmit', data: { type: 'contactForm', formData: typeof formData }): void
}>()

const submit = () => {
  submitted.value = true
  submittedData.value = { ...formData }
  emit('handleSubmit', { type: 'contactForm', formData: { ...formData } })
}
</script>

<style scoped>
.contact-form {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input, textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

textarea {
  height: 100px;
}

.submitted-response {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}
</style>
