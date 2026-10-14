<template>
  <NavBar />
  <div class="layout">
    <RouterView />
  </div>
  <div v-if="store.toast" class="toast">{{ store.toast }}</div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { store, loadProgress } from './store'

onMounted(() => {
  loadProgress()
})
</script>
