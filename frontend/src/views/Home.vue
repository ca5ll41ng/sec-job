<template>
  <div>
    <div style="display: flex; gap: 10px; margin-top: 16px">
      <input
        class="input"
        placeholder="搜索题目 / 面经，回车搜索"
        v-model="q"
        @keydown.enter="goSearch"
      />
      <button class="btn primary" @click="goSearch" style="flex-shrink: 0">搜索</button>
    </div>

    <div class="stats" v-if="s">
      <div class="stat"><div class="num">{{ s.total_questions }}</div><div class="lbl">题库总量</div></div>
      <div class="stat"><div class="num" style="color: var(--green)">{{ s.known }}</div><div class="lbl">已掌握</div></div>
      <div class="stat"><div class="num" style="color: var(--red)">{{ s.unknown }}</div><div class="lbl">没掌握</div></div>
      <div class="stat"><div class="num" style="color: var(--amber)">{{ s.starred }}</div><div class="lbl">收藏</div></div>
    </div>

    <div style="display: flex; gap: 10px; margin: 4px 0 18px; flex-wrap: wrap">
      <button class="btn primary" @click="start(false)">▶️ 顺序刷题</button>
      <button class="btn" @click="startRandom(false)">🔀 随机刷题</button>
      <button class="btn" @click="startRandom(true)">👁️ 背题模式</button>
    </div>

    <h1 class="page-title" style="font-size: 17px; margin-top: 0">题目分类</h1>
    <div class="cats">
      <RouterLink
        v-for="c in s?.categories || []"
        :key="c.name"
        class="cat"
        :to="{ path: '/quiz', query: { cat: c.name } }"
      >
        <div class="name">{{ c.name }}</div>
        <div class="bar"><i :style="{ width: pct(c) + '%' }"></i></div>
        <div class="row">
          <span>{{ c.count }} 题</span>
          <span>{{ c.known ? `已掌握 ${c.known}` : '未开始' }}</span>
        </div>
      </RouterLink>
    </div>

    <template v-if="s?.companies?.length">
      <h1 class="page-title" style="font-size: 17px">面经 · 按企业</h1>
      <div class="chips" style="padding-bottom: 4px">
        <RouterLink
          v-for="c in s.companies"
          :key="c.company"
          class="chip"
          :to="{ path: '/experiences', query: { company: c.company } }"
        >
          {{ c.company }} · {{ c.count }}
        </RouterLink>
      </div>
    </template>

    <div class="empty" v-if="s && !s.total_questions">
      <div class="big">📭</div>
      题库为空<br />
      <small>请参照 <a href="https://github.com/ca5ll41ng/sec-job#readme" target="_blank">项目 README</a> 导入题目</small>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { store, loadHome } from '../store'

const router = useRouter()
const q = ref('')
const s = computed(() => store.home)

function pct(c) {
  return c.count ? Math.round((c.known / c.count) * 100) : 0
}
function goSearch() {
  if (q.value.trim()) router.push({ path: '/search', query: { q: q.value.trim() } })
}
function start(recite) {
  localStorage.setItem('secquiz_recite', recite ? '1' : '0')
  router.push({ path: '/quiz' })
}
function startRandom(recite) {
  localStorage.setItem('secquiz_recite', recite ? '1' : '0')
  router.push({ path: '/quiz', query: { mode: 'random' } })
}

onMounted(() => {
  loadHome()
})
</script>
