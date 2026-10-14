<template>
  <div v-if="e">
    <div class="quiz-top" style="padding-top: 16px">
      <RouterLink to="/experiences" class="btn sm">←</RouterLink>
      <span class="chip">{{ e.company }}</span>
      <span v-if="e.position" class="chip gray">{{ e.position }}</span>
    </div>
    <div class="card">
      <h1 style="font-size: 19px; margin: 4px 0 10px; line-height: 1.5">{{ e.title }}</h1>
      <div style="font-size: 12.5px; color: var(--muted); margin-bottom: 12px; display: flex; gap: 12px; flex-wrap: wrap">
        <span v-if="e.source_site">来源：{{ e.source_site }}</span>
        <a v-if="e.source_url && e.source_url.startsWith('http')" :href="e.source_url" target="_blank">查看原文 ↗</a>
      </div>
      <MdView :src="e.content" />
    </div>
  </div>
  <div v-else class="empty"><div class="big">⏳</div>加载中…</div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import MdView from '../components/MdView.vue'

const route = useRoute()
const e = ref(null)

onMounted(async () => {
  try {
    e.value = await api.get('/api/experiences/' + route.params.id)
  } catch (err) {
    e.value = { title: '加载失败', company: '', content: err.message }
  }
})
</script>
