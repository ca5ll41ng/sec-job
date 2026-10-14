const CLIENT_KEY = 'secquiz_client_id'

export function clientId() {
  if (!localStorage.getItem(CLIENT_KEY)) {
    localStorage.setItem(CLIENT_KEY, crypto.randomUUID())
  }
  return localStorage.getItem(CLIENT_KEY)
}

async function req(method, url, body) {
  const opt = { method, headers: { 'X-Client-Id': clientId() } }
  if (body !== undefined) {
    opt.headers['Content-Type'] = 'application/json'
    opt.body = JSON.stringify(body)
  }
  const r = await fetch(url, opt)
  if (!r.ok) {
    const data = await r.json().catch(() => ({}))
    throw new Error(data.detail || r.statusText)
  }
  return r.json()
}

export const api = {
  get: (u) => req('GET', u),
  post: (u, b) => req('POST', u, b),
  put: (u, b) => req('PUT', u, b),
  del: (u) => req('DELETE', u),
  clientId,
}
