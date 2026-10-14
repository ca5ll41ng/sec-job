<template>
  <div class="md" ref="root" v-html="html"></div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import hljs from 'highlight.js/lib/common'
import { renderMd } from '../md'

const props = defineProps({ src: String })
const root = ref(null)
const html = computed(() => renderMd(props.src))

watch(
  html,
  async () => {
    await nextTick()
    if (!root.value) return
    root.value.querySelectorAll('pre code').forEach((el) => {
      if (el.dataset.hl) return
      el.dataset.hl = '1'
      try {
        hljs.highlightElement(el)
      } catch {
        /* ignore */
      }
    })
  },
  { immediate: true }
)
</script>
