<template>
  <div v-if="loading" class="empty"><div class="big">⏳</div>加载中…</div>

  <div v-else-if="!ids.length" class="empty">
    <div class="big">🎉</div>
    {{ emptyText }}
    <div style="margin-top: 14px"><RouterLink class="btn primary" to="/">返回首页</RouterLink></div>
  </div>

  <div v-else>
    <div class="quiz-top">
      <RouterLink to="/" class="btn sm">←</RouterLink>
      <span class="q-count">{{ idx + 1 }} / {{ ids.length }}</span>
      <span class="chip" v-if="cur" style="max-width: 40vw; overflow: hidden; text-overflow: ellipsis">{{ cur.category }}</span>
      <span style="flex: 1"></span>
      <div class="seg">
        <button :class="{ on: !recite }" @click="setRecite(false)">练习</button>
        <button :class="{ on: recite }" @click="setRecite(true)">背题</button>
      </div>
    </div>
    <div class="q-progress"><i :style="{ width: ((idx + 1) / ids.length) * 100 + '%' }"></i></div>

    <div class="q-card" v-if="cur" @touchstart="onTouchStart" @touchend="onTouchEnd">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px">
        <span class="chip gray">{{ cur.source_type === 'wechat' ? '公众号' : cur.source_type === 'manual' ? '手动添加' : '面试题库' }}</span>
        <a v-if="cur.source_url" :href="cur.source_url" target="_blank" class="chip gray" style="text-decoration: none">原文 ↗</a>
      </div>
      <h1 class="q-title">{{ cur.title }}</h1>

      <div v-if="recite || revealed" class="q-answer"><MdView :src="cur.answer" /></div>
      <div v-else class="q-answer-mask" @click="revealed = true">
        <div style="font-size: 26px; margin-bottom: 6px">🤔</div>
        先自己想一想<br />点击这里显示答案
      </div>

      <div class="q-actions">
        <button class="btn" :style="prog.starred ? 'background:var(--amber-weak);border-color:transparent;color:var(--amber)' : ''" @click="toggleStar">
          {{ prog.starred ? '⭐ 已收藏' : '☆ 收藏' }}
        </button>
        <button class="btn" :class="prog.status === 'known' ? 'ghost-green' : ''" @click="markKnown">
          {{ prog.status === 'known' ? '✅ 已掌握' : '👍 掌握' }}
        </button>
        <button class="btn" :class="prog.status === 'unknown' ? 'ghost-red' : ''" @click="markUnknown">
          {{ prog.status === 'unknown' ? '❌ 已标记' : '👎 没掌握' }}
        </button>
      </div>
    </div>

    <div class="q-nav">
      <button class="btn" style="flex: 1" :disabled="idx <= 0" @click="prev">上一题</button>
      <button class="btn primary" style="flex: 2" @click="next">{{ idx >= ids.length - 1 ? '完成 🎉' : '下一题' }}</button>
    </div>

    <div v-if="done" class="modal-mask" @click.self="done = false">
      <div class="modal" style="text-align: center">
        <h3>🎉 本轮完成</h3>
        <p style="color: var(--muted)">共刷完 {{ ids.length }} 题，快去复习错题本吧</p>
        <div style="display: flex; gap: 10px; margin-top: 14px">
          <button class="btn" style="flex: 1" @click="done = false">继续浏览</button>
          <button class="btn primary" style="flex: 1" @click="restartRandom">🔀 再来一轮</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getQuestion, getQuizIds } from '../data'
import { progOf, mark, toast } from '../store'
import MdView from '../components/MdView.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const ids = ref([])
const idx = ref(0)
const details = ref({})
const recite = ref(localStorage.getItem('secquiz_recite') === '1')
const revealed = ref(false)
const done = ref(false)

const cur = computed(() => details.value[ids.value[idx.value]])
const prog = computed(() => progOf(cur.value?.id))
const emptyText = computed(() =>
  route.query.from === 'wrong'
    ? '太棒了，暂无错题'
    : route.query.from === 'star'
      ? '还没有收藏题目，刷题时点 ⭐ 收藏'
      : '没有找到可刷的题目'
)

function setRecite(v) {
  recite.value = v
  localStorage.setItem('secquiz_recite', v ? '1' : '0')
}

async function loadIds() {
  loading.value = true
  done.value = false
  const p = route.query
  try {
    ids.value = await getQuizIds({
      category: p.cat,
      shuffle: p.mode === 'random',
      filter: p.from,
      ids: p.ids,
    })
  } catch (e) {
    toast('加载失败：' + e.message)
    ids.value = []
  }
  idx.value = 0
  details.value = {}
  revealed.value = false
  if (ids.value.length) await loadCur()
  loading.value = false
}

async function loadCur() {
  const id = ids.value[idx.value]
  if (!id || details.value[id]) return
  try {
    details.value[id] = await getQuestion(id)
  } catch (e) {
    toast('加载题目失败：' + e.message)
  }
}

async function next() {
  if (idx.value >= ids.value.length - 1) {
    done.value = true
    return
  }
  idx.value++
  revealed.value = false
  await loadCur()
}
function prev() {
  if (idx.value > 0) {
    idx.value--
    revealed.value = false
    loadCur()
  }
}

async function setMark(status) {
  const id = cur.value.id
  const before = progOf(id).status
  if (status === 'unknown' && !revealed.value && !recite.value) revealed.value = true
  await mark(id, { status })
  if (status === 'known' && before !== 'known') setTimeout(next, 300)
}
const markKnown = () => setMark('known')
const markUnknown = () => setMark('unknown')
const toggleStar = () => mark(cur.value.id, { starred: !progOf(cur.value.id).starred })

function restartRandom() {
  done.value = false
  router.replace({ path: '/quiz', query: { ...route.query, mode: 'random' } })
}

function onKey(e) {
  if (e.key === 'ArrowRight') next()
  else if (e.key === 'ArrowLeft') prev()
  else if (e.key === ' ') {
    e.preventDefault()
    revealed.value = !revealed.value
  }
}
let touchX = 0
function onTouchStart(e) {
  touchX = e.changedTouches[0].clientX
}
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchX
  if (Math.abs(dx) > 60) dx < 0 ? next() : prev()
}

onMounted(() => {
  loadIds()
  window.addEventListener('keydown', onKey)
})
onUnmounted(() => window.removeEventListener('keydown', onKey))
watch(
  () => route.query,
  () => {
    if (route.path === '/quiz') loadIds()
  }
)
</script>
