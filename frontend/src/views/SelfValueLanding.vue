<template>
  <div class="page-shell">
    <div class="page-container">
      <div class="ui-eyebrow">自我价值梳理</div>

      <h1 class="ui-title">
        也许你不是突然迷失了，而是过去那套支撑你的身份，正在失去力量。
      </h1>

      <p class="ui-subtitle">
        通过一组问题与专属报告，帮你整理那些正在松动的部分，并重新看见你的价值线索。
      </p>

      <div class="ui-actions">
        <button class="ui-btn-primary" type="button" @click="goIntro">
          开始这次梳理
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelfValueLanding',
  methods: {
    goIntro() {
      this.$router.push('/self-value/intro')
    }
  }
}
</script>

<style scoped>
</style>
