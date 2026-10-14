<template>
  <h1 class="page-title">搜索</h1>
  <p class="page-sub">关键词「{{ q }}」的结果</p>

  <template v-if="r">
    <template v-if="r.questions.length">
      <h2 style="font-size: 16px; margin: 0 0 10px">题目 ({{ r.questions.length }})</h2>
      <div class="list" style="margin-bottom: 20px">
        <RouterLink v-for="item in r.questions" :key="item.id" class="row-item" :to="{ path: '/quiz', query: { ids: item.id } }">
          <span class="chip gray">{{ item.category }}</span>
          <div class="t">{{ item.title }}</div>
        </RouterLink>
      </div>
    </template>
    <template v-if="r.experiences.length">
      <h2 style="font-size: 16px; margin: 0 0 10px">面经 ({{ r.experiences.length }})</h2>
      <div class="list">
        <RouterLink v-for="item in r.experiences" :key="item.id" class="row-item" :to="'/experiences/' + item.id">
          <span class="chip">{{ item.company }}</span>
          <div class="t">{{ item.title }}</div>
        </RouterLink>
      </div>
    </template>
    <div v-if="!r.questions.length && !r.experiences.length" class="empty">
      <div class="big">🔍</div>没有找到相关内容
    </div>
  </template>
  <div v-else class="empty"><div class="big">⏳</div>搜索中…</div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { searchAll } from '../data'

const route = useRoute()
const q = ref(route.query.q || '')
const r = ref(null)

async function load() {
  r.value = null
  if (!q.value) return
  r.value = await searchAll(q.value)
}

onMounted(load)
watch(
  () => route.query.q,
  (v) => {
    q.value = v || ''
    load()
  }
)
</script>
