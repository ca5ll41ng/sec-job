<template>
  <header class="topbar">
    <RouterLink to="/" class="logo">🛡️ <span>安全面试刷题</span></RouterLink>
    <nav>
      <RouterLink to="/">题库</RouterLink>
      <RouterLink to="/review">复习</RouterLink>
      <RouterLink to="/experiences">面经</RouterLink>
      <RouterLink to="/settings">设置</RouterLink>
    </nav>
    <span class="spacer"></span>
    <input
      class="input search-input"
      placeholder="搜索题目 / 面经…"
      @keydown.enter="$router.push({ path: '/search', query: { q: $event.target.value.trim() } })"
    />
  </header>
  <nav class="tabbar">
    <RouterLink to="/"><span class="ic">📚</span>题库</RouterLink>
    <RouterLink to="/review"><span class="ic">🔁</span>复习</RouterLink>
    <RouterLink to="/experiences"><span class="ic">💼</span>面经</RouterLink>
    <RouterLink to="/settings"><span class="ic">⚙️</span>设置</RouterLink>
  </nav>
</template>
