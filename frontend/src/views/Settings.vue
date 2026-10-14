<template>
  <h1 class="page-title">设置</h1>
  <p class="page-sub">当前版本 v{{ APP_VERSION }}</p>

  <div class="card" style="margin-bottom: 14px">
    <h3 style="margin: 0 0 8px">刷题记录</h3>
    <p style="font-size: 13.5px; color: var(--muted); margin: 0 0 10px">
      <template v-if="!isOffline">进度保存在服务器上，同一浏览器自动同步；换浏览器或设备会重新开始记录。</template>
      <template v-else>当前为离线模式，进度保存在本机。</template>
    </p>
    <button class="btn" @click="clearProgress">🗑️ 清空刷题记录</button>
  </div>

  <div v-if="!isOffline" class="card" style="margin-bottom: 14px">
    <h3 style="margin: 0 0 8px">导入公众号文章为题目</h3>
    <div class="form-row">
      <input class="input" v-model="wxUrl" placeholder="https://mp.weixin.qq.com/s/..." />
    </div>
    <div class="form-row">
      <input class="input" v-model="wxCat" placeholder="分类名（可选，默认：公众号收录）" />
    </div>
    <div style="display: flex; gap: 10px; align-items: center">
      <label style="font-size: 13.5px; color: var(--muted); display: flex; align-items: center; gap: 5px">
        <input type="checkbox" v-model="wxSplit" /> 按小标题切分为多题
      </label>
      <button class="btn primary" style="margin-left: auto" :disabled="wxImporting" @click="importWechat">
        {{ wxImporting ? '导入中…' : '导入' }}
      </button>
    </div>
  </div>

  <div class="card">
    <h3 style="margin: 0 0 8px">关于</h3>
    <div style="font-size: 13.5px; color: var(--muted); line-height: 2.2">
      题库来源：<a href="https://github.com/duckpigdog/Sec-Interview" target="_blank">Sec-Interview</a><br />
      项目地址：<a href="https://github.com/ca5ll41ng/sec-job" target="_blank">ca5ll41ng/sec-job</a><br />
      批量导入题目或面经请参照项目 README，在服务器端操作。
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { clearAllProgress, importWechat as importWechatApi, offline } from '../data'
import { toast, loadProgress } from '../store'
import { APP_VERSION } from '../update'

const isOffline = offline
const wxUrl = ref('')
const wxCat = ref('')
const wxSplit = ref(true)
const wxImporting = ref(false)

async function clearProgress() {
  if (!confirm('确定清空全部刷题记录（掌握/错题/收藏）？')) return
  try {
    await clearAllProgress()
    toast('已清空')
    loadProgress()
  } catch (e) {
    toast('操作失败：' + e.message)
  }
}

async function importWechat() {
  if (!wxUrl.value.trim()) return toast('请填写文章链接')
  wxImporting.value = true
  try {
    const r = await importWechatApi({
      url: wxUrl.value.trim(),
      split: wxSplit.value,
      category: wxCat.value.trim() || null,
    })
    toast(`✅ 已导入 ${r.imported} 题`)
    wxUrl.value = ''
  } catch (e) {
    toast('导入失败：' + e.message)
  } finally {
    wxImporting.value = false
  }
}
</script>
