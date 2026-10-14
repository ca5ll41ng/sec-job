<template>
  <NavBar />
  <div class="layout">
    <RouterView />
  </div>
  <div v-if="store.toast" class="toast">{{ store.toast }}</div>

  <!-- 强制更新：无关闭入口，仅提供下载链接 -->
  <div v-if="store.updateInfo" class="update-mask">
    <div class="update-card">
      <div style="font-size: 42px">🔄</div>
      <h3 style="margin: 10px 0 4px">发现新版本 v{{ store.updateInfo.latest }}</h3>
      <p style="color: var(--muted); font-size: 14px; margin: 0 0 18px">
        当前版本 v{{ APP_VERSION }}，请先更新再继续使用
      </p>
      <a class="btn primary block" :href="store.updateInfo.url">前往下载新版本 ↗</a>
      <p style="color: var(--muted); font-size: 12px; margin: 12px 0 0">
        安卓：下载新 APK 直接覆盖安装（进度不丢失）
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { store, loadProgress } from './store'
import { checkUpdate, APP_VERSION } from './update'

onMounted(async () => {
  loadProgress()
  const upd = await checkUpdate()
  if (upd) store.updateInfo = upd
})
</script>
