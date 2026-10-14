import { reactive } from 'vue'
import { getHome, getProgressMap, saveProgress } from './data'

export const store = reactive({
  progress: {},
  home: null,
  toast: '',
})

let toastTimer
export function toast(msg) {
  store.toast = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (store.toast = ''), 2200)
}

export async function loadHome() {
  store.home = await getHome()
}

export async function loadProgress() {
  store.progress = await getProgressMap()
}

export function progOf(id) {
  return store.progress[id] || { status: 'none', starred: false }
}

export async function mark(id, { status, starred }) {
  const cur = progOf(id)
  const next = {
    status: status === undefined ? cur.status : status,
    starred: starred === undefined ? cur.starred : starred,
  }
  store.progress[id] = next
  try {
    await saveProgress(id, next)
  } catch (e) {
    toast('保存进度失败：' + e.message)
  }
}
