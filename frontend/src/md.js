import { marked } from 'marked'
import DOMPurify from 'dompurify'

DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  // file:// (APK 离线包) 下不做新窗口打开，交给 WebView 拦截后跳系统浏览器
  if (location.protocol === 'file:') return
  if (node.tagName === 'A' && node.getAttribute('href')) {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener nofollow')
  }
})

export function renderMd(src) {
  const html = marked.parse(src || '', { breaks: true })
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target'] })
}
