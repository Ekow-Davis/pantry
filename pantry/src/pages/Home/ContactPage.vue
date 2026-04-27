<script setup lang="ts">
import { ref } from 'vue'
import { Mail, MessageSquare, Send } from 'lucide-vue-next'

const form = ref({ name: '', email: '', subject: '', message: '' })
const sent = ref(false)

function submit() {
  // TODO: wire to backend / email service
  sent.value = true
}
</script>

<template>
  <section class="section">
    <div class="container max-w-2xl">
      <div class="text-center mb-12">
        <span class="badge badge-primary mb-4">Contact</span>
        <h1 class="text-5xl font-black mb-4" style="font-family:var(--font-display)">Get in <span style="color:var(--color-primary)">touch</span></h1>
        <p class="text-lg" style="color:var(--color-text-muted)">Questions, feedback, or partnership ideas — we'd love to hear from you.</p>
      </div>

      <div v-if="!sent" class="card p-8 animate-fade-up">
        <div class="flex flex-col gap-5">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Name</label>
              <input v-model="form.name" class="input" placeholder="Your name" />
            </div>
            <div>
              <label class="label">Email</label>
              <input v-model="form.email" type="email" class="input" placeholder="your@email.com" />
            </div>
          </div>
          <div>
            <label class="label">Subject</label>
            <input v-model="form.subject" class="input" placeholder="What's this about?" />
          </div>
          <div>
            <label class="label">Message</label>
            <textarea v-model="form.message" class="input resize-none h-36" placeholder="Tell us more..."></textarea>
          </div>
          <button class="btn-primary self-end" @click="submit">
            Send Message <Send class="w-4 h-4" />
          </button>
        </div>
      </div>

      <div v-else class="card p-12 text-center animate-scale-in">
        <div class="text-6xl mb-4">🎉</div>
        <h2 class="text-2xl font-black mb-2" style="font-family:var(--font-display)">Message sent!</h2>
        <p style="color:var(--color-text-muted)">We'll get back to you as soon as possible.</p>
      </div>
    </div>
  </section>
</template>
