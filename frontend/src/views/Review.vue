<template>
  <h1 class="page-title">复习</h1>
  <p class="page-sub">错题与收藏集中重练</p>

  <div class="seg" style="margin-bottom: 14px">
    <button :class="{ on: tab === 'wrong' }" @click="switchTab('wrong')">❌ 错题本</button>
    <button :class="{ on: tab === 'star' }" @click="switchTab('star')">⭐ 收藏</button>
  </div>

  <div style="display: flex; gap: 10px; margin-bottom: 14px">
    <button class="btn primary" @click="startQuiz" :disabled="!items.length">
      开始重练 ({{ items.length }})
    </button>
    <button v-if="tab === 'wrong'" class="btn" @click="clearWrong" :disabled="!items.length">
      全部标为已掌握
    </button>
  </div>

  <div class="list" v-if="items.length">
    <RouterLink v-for="q in items" :key="q.id" class="row-item" :to="{ path: '/quiz', query: { from: tab } }">
      <span class="chip gray">{{ q.category }}</span>
      <div class="t">{{ q.title }}</div>
    </RouterLink>
  </div>
  <div v-else-if="!loading" class="empty">
    <div class="big">{{ tab === 'wrong' ? '🎉' : '⭐' }}</div>
    {{ tab === 'wrong' ? '太棒了，暂无错题' : '还没有收藏题目' }}
  </div>
  <div v-else class="empty"><div class="big">⏳</div>加载中…</div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listQuestions, saveProgress } from '../data'
import { toast, loadProgress } from '../store'

const route = useRoute()
const router = useRouter()
const tab = ref(route.query.tab === 'star' ? 'star' : 'wrong')
const items = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    items.value = await listQuestions({ type: tab.value })
  } catch (e) {
    toast('加载失败：' + e.message)
  }
  loading.value = false
}

function switchTab(t) {
  tab.value = t
  load()
}
function startQuiz() {
  router.push({ path: '/quiz', query: { from: tab.value } })
}
async function clearWrong() {
  try {
    for (const q of items.value) await saveProgress(q.id, { status: 'known' })
    toast('已全部标记为掌握 ✅')
    await load()
    loadProgress()
  } catch (e) {
    toast('操作失败：' + e.message)
  }
}

onMounted(load)
</script>
