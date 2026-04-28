<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import ToastContainer from '@/components/general/ToastContainer.vue'

const { initTheme } = useTheme()
onMounted(() => initTheme())
</script>

<template>
  <!--
    No <Transition> here — layout components (HomeLayout, AppLayout etc.)
    are multi-element trees and cannot be animated at this level.
    Page transitions are handled inside each layout's own <RouterView>.
  -->
  <RouterView />
  <ToastContainer />
</template>