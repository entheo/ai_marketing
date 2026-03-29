<template>
  <div
    class="light-markdown-block"
    v-html="renderedHtml"
  ></div>
</template>

<script>
import { renderLightMarkdown } from '@/utils/lightMarkdown'

export default {
  name: 'LightMarkdownBlock',

  props: {
    content: {
      type: String,
      default: ''
    }
  },

  computed: {
    renderedHtml() {
      return renderLightMarkdown(this.content)
    }
  }
}
</script>

<style scoped>
.light-markdown-block :deep(p) {
  margin: 0;
}

.light-markdown-block :deep(p + p) {
  margin-top: 12px;
}

.light-markdown-block :deep(ul),
.light-markdown-block :deep(ol) {
  margin: 0;
  padding-left: 1.35em;
}

.light-markdown-block :deep(p + ul),
.light-markdown-block :deep(p + ol),
.light-markdown-block :deep(ul + p),
.light-markdown-block :deep(ol + p),
.light-markdown-block :deep(ul + ul),
.light-markdown-block :deep(ol + ol),
.light-markdown-block :deep(ul + ol),
.light-markdown-block :deep(ol + ul) {
  margin-top: 12px;
}

.light-markdown-block :deep(li + li) {
  margin-top: 8px;
}

.light-markdown-block :deep(strong) {
  font-weight: 650;
}
</style>
