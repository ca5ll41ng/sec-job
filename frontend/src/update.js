const REPO = 'ca5ll41ng/sec-job'

// 由 vite define 注入（读取根目录 VERSION 文件）
const APP_VERSION =
  typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '0.0.0'

export { APP_VERSION }

function cmpVer(a, b) {
  const pa = String(a).split('.').map(Number)
  const pb = String(b).split('.').map(Number)
  for (let i = 0; i < 3; i++) {
    const d = (pa[i] || 0) - (pb[i] || 0)
    if (d) return d
  }
  return 0
}

/**
 * 启动时检查 GitHub 最新 Release。
 * 返回 null（无更新/无网络）或 { latest, url }。
 * 有更新时由 App.vue 强制弹出全屏更新提示。
 */
export async function checkUpdate() {
  try {
    const ctl = new AbortController()
    const t = setTimeout(() => ctl.abort(), 5000)
    const r = await fetch(`https://api.github.com/repos/${REPO}/releases/latest`, {
      signal: ctl.signal,
      headers: { Accept: 'application/vnd.github+json' },
    })
    clearTimeout(t)
    if (!r.ok) return null
    const rel = await r.json()
    const latest = String(rel.tag_name || '').replace(/^v/i, '')
    if (!/^\d+(\.\d+){0,2}$/.test(latest)) return null
    if (cmpVer(latest, APP_VERSION) > 0) {
      return { latest, url: rel.html_url || `https://github.com/${REPO}/releases/latest` }
    }
  } catch {
    /* 无网络或接口不可达时静默跳过 */
  }
  return null
}
