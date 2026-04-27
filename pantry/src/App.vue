<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import ToastContainer from '@/components/general/ToastContainer.vue'

const { initTheme } = useTheme()
onMounted(() => initTheme())
</script>

<template>
  <RouterView v-slot="{ Component, route }">
    <Transition name="page" mode="out-in">
      <component :is="Component" :key="route.path" />
    </Transition>
  </RouterView>
  <ToastContainer />
</template>
