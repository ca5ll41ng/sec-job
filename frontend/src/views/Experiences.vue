<template>
  <div style="display: flex; align-items: center; gap: 10px; margin-top: 16px">
    <h1 class="page-title" style="margin: 0; flex: 1">安全面经</h1>
    <button v-if="!isOffline" class="btn primary sm" @click="showImport = true">＋ 导入</button>
  </div>
  <p class="page-sub">按企业分类的安全工程师面经</p>

  <div v-if="isOffline" class="card" style="margin-bottom: 12px; font-size: 13.5px; color: var(--muted)">
    📱 离线模式下没有面经数据。面经收录在电脑版里，同一局域网内用手机浏览器访问
    <code>http://电脑IP:8000</code> 即可查看完整版。
  </div>

  <input v-if="!isOffline" class="input" style="margin-bottom: 12px" placeholder="搜索面经内容，回车确认" v-model="kw" @keydown.enter="load" />

  <div class="chips" v-if="companies.length">
    <span class="chip" :class="{ on: company === '' }" @click="setCompany('')">全部 {{ total }}</span>
    <span
      v-for="c in companies"
      :key="c.company"
      class="chip"
      :class="{ on: company === c.company }"
      @click="setCompany(c.company)"
    >
      {{ c.company }} {{ c.count }}
    </span>
  </div>

  <div class="list" v-if="items.length">
    <RouterLink v-for="e in items" :key="e.id" class="row-item" :to="'/experiences/' + e.id">
      <div>
        <span class="chip">{{ e.company }}</span>
        <span v-if="e.position" class="chip gray" style="margin-left: 6px">{{ e.position }}</span>
      </div>
      <div class="t">{{ e.title }}</div>
      <div class="meta">
        <span v-if="e.source_site">🌐 {{ e.source_site }}</span>
        <span>入库 {{ (e.created_at || '').slice(0, 10) }}</span>
      </div>
      <div class="excerpt">{{ e.excerpt }}</div>
    </RouterLink>
  </div>
  <div v-else-if="!loading" class="empty">
    <div class="big">💼</div>
    暂无面经<br />
    <small>
      点击右上角「导入」，粘贴面经链接或文本，<br />
      填写企业名即可按企业分类保存
    </small>
  </div>
  <div v-else class="empty"><div class="big">⏳</div>加载中…</div>

  <div v-if="showImport" class="modal-mask" @click.self="showImport = false">
    <div class="modal">
      <h3>导入面经</h3>
      <div class="form-row">
        <label>导入方式</label>
        <div class="seg">
          <button :class="{ on: mode === 'url' }" @click="mode = 'url'">网页链接</button>
          <button :class="{ on: mode === 'text' }" @click="mode = 'text'">粘贴文本</button>
        </div>
      </div>
      <div class="form-row" v-if="mode === 'url'">
        <label>文章链接（公众号 / 牛客 / 知乎 / CSDN 等）</label>
        <input class="input" v-model="form.url" placeholder="https://mp.weixin.qq.com/s/..." />
      </div>
      <div class="form-row" v-else>
        <label>面经正文</label>
        <textarea class="input" v-model="form.text" placeholder="粘贴面经内容…"></textarea>
      </div>
      <div class="form-row">
        <label>企业 *</label>
        <input class="input" v-model="form.company" placeholder="如：腾讯" />
      </div>
      <div class="form-row">
        <label>岗位</label>
        <input class="input" v-model="form.position" placeholder="如：渗透测试工程师（留空自动识别）" />
      </div>
      <div style="display: flex; gap: 10px; margin-top: 16px">
        <button class="btn" style="flex: 1" @click="showImport = false">取消</button>
        <button class="btn primary" style="flex: 1" :disabled="importing" @click="doImport">
          {{ importing ? '导入中…' : '导入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getCompanies, importExperience, listExperiences, offline } from '../data'
import { toast } from '../store'

const route = useRoute()
const isOffline = offline
const company = ref(route.query.company || '')
const companies = ref([])
const items = ref([])
const total = ref(0)
const loading = ref(true)
const showImport = ref(false)
const mode = ref('url')
const importing = ref(false)
const kw = ref('')
const form = ref({ url: '', text: '', company: '', position: '' })

async function load() {
  loading.value = true
  try {
    const d = await listExperiences({ company: company.value, q: kw.value.trim() })
    items.value = d.items
    total.value = d.total
  } catch (e) {
    toast('加载失败：' + e.message)
  }
  loading.value = false
}

async function loadCompanies() {
  try {
    companies.value = await getCompanies()
  } catch {
    companies.value = []
  }
}

function setCompany(c) {
  company.value = c
  load()
}

async function doImport() {
  if (mode.value === 'url' && !form.value.url.trim()) return toast('请填写链接')
  if (mode.value === 'text' && !form.value.text.trim()) return toast('请粘贴正文')
  if (!form.value.company.trim()) return toast('请填写企业名')
  importing.value = true
  try {
    await importExperience({
      url: mode.value === 'url' ? form.value.url.trim() : null,
      text: mode.value === 'text' ? form.value.text : null,
      company: form.value.company.trim(),
      position: form.value.position.trim() || null,
    })
    toast('✅ 导入成功')
    showImport.value = false
    form.value = { url: '', text: '', company: '', position: '' }
    await Promise.all([loadCompanies(), load()])
  } catch (e) {
    toast('导入失败：' + e.message)
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadCompanies(), load()])
})
</script>
