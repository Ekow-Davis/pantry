<script setup lang="ts">
import { ref } from 'vue'
import { PlusCircle, Upload } from 'lucide-vue-next'
import api from '@/composables/useApi'
import { useNotificationsStore } from '@/stores/notifications'
import { useRouter } from 'vue-router'

const notify = useNotificationsStore()
const router = useRouter()

const form = ref({
  name: '',
  description: '',
  category_slugs: [] as string[],
})
const loading = ref(false)

const categories = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'any']

function toggleCat(slug: string) {
  const idx = form.value.category_slugs.indexOf(slug)
  if (idx === -1) form.value.category_slugs.push(slug)
  else form.value.category_slugs.splice(idx, 1)
}

async function submit() {
  if (!form.value.name || !form.value.category_slugs.length) {
    notify.warning('Please provide a name and at least one category.')
    return
  }
  loading.value = true
  try {
    await api.post('/api/v1/meals/contribute', form.value)
    notify.success('Meal submitted for review. Thank you!')
    router.push('/app/meals')
  } catch (e: any) {
    notify.error(e.response?.data?.detail || 'Submission failed.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Contribute a Meal</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">Submit a recipe to expand the MealWise library. It'll be reviewed before going live.</p>
    </div>

    <div class="card p-6 animate-fade-up delay-100">
      <div class="flex flex-col gap-5">
        <div>
          <label class="label">Meal Name <span style="color:var(--color-danger)">*</span></label>
          <input v-model="form.name" class="input" placeholder="e.g. Waakye with Fried Fish" />
        </div>

        <div>
          <label class="label">Description</label>
          <textarea v-model="form.description" class="input resize-none h-28" placeholder="A brief description of the meal..."></textarea>
        </div>

        <div>
          <label class="label">Categories <span style="color:var(--color-danger)">*</span></label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="cat in categories"
              :key="cat"
              class="px-4 py-2 rounded-full text-sm font-medium transition-all"
              :style="form.category_slugs.includes(cat)
                ? 'background:var(--color-primary); color:#fff;'
                : 'background:var(--color-surface); color:var(--color-text-muted); border:1.5px solid var(--color-border)'"
              @click="toggleCat(cat)"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <!-- Photo upload placeholder -->
        <div class="flex items-center justify-center gap-3 p-6 rounded-2xl border-2 border-dashed cursor-pointer"
          style="border-color:var(--color-border); background:var(--color-surface)">
          <Upload class="w-5 h-5" style="color:var(--color-text-faint)" />
          <p class="text-sm" style="color:var(--color-text-muted)">Upload a photo <span style="color:var(--color-text-faint)">(optional — coming soon)</span></p>
        </div>

        <div class="flex justify-end gap-3">
          <button class="btn-surface" @click="$router.back()">Cancel</button>
          <button class="btn-primary" :disabled="loading" @click="submit">
            <span v-if="loading" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
            <template v-else><PlusCircle class="w-4 h-4" /> Submit for Review</template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
