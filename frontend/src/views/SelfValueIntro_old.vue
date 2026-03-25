
<template>
  <div class="page-shell">
    <div class="page-container">
      <div class="ui-eyebrow">开始之前</div>

      <h1 class="ui-title">
        这里没有标准答案，你也不需要把自己表达得完整。
      </h1>

      <p class="ui-subtitle">
        哪怕有些地方还很模糊，也可以从你最有感觉的部分开始。
      </p>

      <div class="ui-actions">
        <button class="ui-btn-secondary" type="button" @click="goBack">
          返回上一页
        </button>
        <button class="ui-btn-primary" type="button" @click="goQuestions">
          进入问题
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelfValueIntro',
  methods: {
    goBack() {
      this.$router.back()
    },
    goQuestions() {
      this.$router.push('/self-value/questions')
    }
  }
}
</script>

<style scoped>
</style>

