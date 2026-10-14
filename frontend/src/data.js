import { api } from './api'
import localQuestions from './data/questions.json'

/**
 * 数据层：自动选择「服务器模式」或「离线模式」。
 * - file:// 协议（APK 内）→ 纯离线：题目来自打包 JSON，进度存 localStorage
 * - http(s) → 先探测服务器，可用则走后端 API（含面经/导入功能），否则同样离线
 */
export const isFile = location.protocol === 'file:'
let serverOk = false

const readyPromise = (async () => {
  if (isFile) return
  try {
    const ctl = new AbortController()
    const t = setTimeout(() => ctl.abort(), 2500)
    const r = await fetch('/api/home', { signal: ctl.signal })
    clearTimeout(t)
    serverOk = r.ok
  } catch {
    serverOk = false
  }
})()

async function ensure() {
  await readyPromise
}
export async function serverMode() {
  await ensure()
  return serverOk
}
export const offline = isFile

// ---------- 本地题库 ----------
const sortedLocal = [...localQuestions].sort((a, b) => (a.sort_key || '').localeCompare(b.sort_key || ''))
const localById = new Map(localQuestions.map((q) => [q.id, q]))

// ---------- 本地进度 ----------
const LS_KEY = 'secquiz_local_progress'

function lsAll() {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) || '{}')
  } catch {
    return {}
  }
}
function lsSave(all) {
  localStorage.setItem(LS_KEY, JSON.stringify(all))
}

function withProg(q) {
  const p = lsAll()[q.id] || { status: 'none', starred: false }
  return { ...q, status: p.status, starred: !!p.starred }
}

function localHome() {
  const map = new Map()
  for (const q of sortedLocal) {
    if (!map.has(q.category)) {
      map.set(q.category, { name: q.category, count: 0, known: 0, unknown: 0, sort: q.sort_key })
    }
    map.get(q.category).count++
  }
  const prog = lsAll()
  let known = 0
  let unknown = 0
  let starred = 0
  for (const [qid, p] of Object.entries(prog)) {
    const q = localById.get(Number(qid))
    if (!q) continue
    const c = map.get(q.category)
    if (p.status === 'known') {
      c.known++
      known++
    } else if (p.status === 'unknown') {
      c.unknown++
      unknown++
    }
    if (p.starred) starred++
  }
  return {
    total_questions: localQuestions.length,
    known,
    unknown,
    starred,
    total_experiences: 0,
    companies: [],
    categories: [...map.values()],
  }
}

// ---------- 对外 API（与后端接口同形） ----------
export async function getHome() {
  await ensure()
  return serverOk ? api.get('/api/home') : localHome()
}

export async function getProgressMap() {
  await ensure()
  return serverOk ? api.get('/api/progress') : lsAll()
}

export async function saveProgress(qid, { status, starred }) {
  await ensure()
  if (serverOk) {
    await api.put(`/api/progress/${qid}`, { status, starred })
    return
  }
  const all = lsAll()
  const cur = all[qid] || { status: 'none', starred: false }
  const next = {
    status: status === undefined ? cur.status : status,
    starred: starred === undefined ? cur.starred : starred,
  }
  if (next.status === 'none' && !next.starred) delete all[qid]
  else all[qid] = next
  lsSave(all)
}

export async function clearAllProgress() {
  await ensure()
  if (serverOk) {
    await api.del('/api/progress?confirm=true')
    return
  }
  localStorage.removeItem(LS_KEY)
}

export async function getQuizIds({ category, shuffle, filter, ids } = {}) {
  await ensure()
  if (serverOk) {
    const p = new URLSearchParams()
    if (category) p.set('category', category)
    if (shuffle) p.set('shuffle', '1')
    if (filter && filter !== 'all') p.set('filter', filter)
    if (ids) p.set('ids', ids)
    return (await api.get('/api/quiz-ids?' + p.toString())).ids
  }
  if (ids) return ids.split(',').map(Number).filter(Number.isFinite)
  const prog = lsAll()
  let list = sortedLocal
  if (filter === 'wrong') list = list.filter((q) => prog[q.id]?.status === 'unknown')
  else if (filter === 'star') list = list.filter((q) => prog[q.id]?.starred)
  if (category && category !== 'all') list = list.filter((q) => q.category === category)
  const arr = list.map((q) => q.id)
  return shuffle ? arr.sort(() => Math.random() - 0.5) : arr
}

export async function getQuestion(id) {
  await ensure()
  if (serverOk) return api.get('/api/questions/' + id)
  const q = localById.get(Number(id))
  if (!q) throw new Error('题目不存在')
  return withProg(q)
}

export async function listQuestions({ type, q } = {}) {
  await ensure()
  if (serverOk) {
    const p = new URLSearchParams({ page_size: '500' })
    if (type) p.set('type', type)
    if (q) p.set('q', q)
    return (await api.get('/api/questions?' + p.toString())).items
  }
  let list = sortedLocal.map(withProg)
  if (type === 'wrong') list = list.filter((x) => x.status === 'unknown')
  else if (type === 'star') list = list.filter((x) => x.starred)
  if (q) list = list.filter((x) => x.title.includes(q) || (x.answer || '').includes(q))
  return list
}

export async function searchAll(q) {
  await ensure()
  if (serverOk) return api.get('/api/search?q=' + encodeURIComponent(q))
  const kw = q.trim().toLowerCase()
  const questions = sortedLocal
    .filter((x) => x.title.toLowerCase().includes(kw) || (x.answer || '').toLowerCase().includes(kw))
    .slice(0, 30)
    .map(({ id, category, title }) => ({ id, category, title }))
  return { questions, experiences: [] }
}

// ---------- 面经（仅服务器模式可用） ----------
export async function getCompanies() {
  await ensure()
  return serverOk ? (await api.get('/api/experiences/companies')).items : []
}

export async function listExperiences({ company, q } = {}) {
  await ensure()
  if (serverOk) {
    const p = new URLSearchParams()
    if (company) p.set('company', company)
    if (q) p.set('q', q)
    return api.get('/api/experiences?' + p.toString())
  }
  return { total: 0, items: [] }
}

export async function getExperience(id) {
  await ensure()
  if (!serverOk) throw new Error('离线模式下无面经数据')
  return api.get('/api/experiences/' + id)
}

export async function importExperience(payload) {
  await ensure()
  if (!serverOk) throw new Error('离线模式下不支持导入，请在电脑上打开完整版')
  return api.post('/api/experiences/import', payload)
}

export async function importWechat(payload) {
  await ensure()
  if (!serverOk) throw new Error('离线模式下不支持导入，请在电脑上打开完整版')
  return api.post('/api/questions/import-wechat', payload)
}
