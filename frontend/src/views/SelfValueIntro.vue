<template>
  <div class="intro-breath-page">
    <div class="intro-gradient intro-gradient-a"></div>
    <div class="intro-gradient intro-gradient-b"></div>
    <div class="intro-gradient intro-gradient-c"></div>

    <div class="page-shell intro-shell">
      <div class="page-container intro-container">
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
.intro-breath-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #f7f5f2;
}

.intro-shell {
  position: relative;
  z-index: 2;
}

.intro-container {
  position: relative;
  z-index: 2;
}

.intro-gradient {
  position: absolute;
  border-radius: 999px;
  filter: blur(80px);
  opacity: 0.42;
  pointer-events: none;
  transform-origin: center;
  animation: floatBreath 16s ease-in-out infinite;
}

.intro-gradient-a {
  width: 520px;
  height: 520px;
  left: -120px;
  top: -80px;
  background: radial-gradient(circle, rgba(182, 207, 255, 0.75) 0%, rgba(182, 207, 255, 0) 70%);
  animation-delay: 0s;
}

.intro-gradient-b {
  width: 520px;
  height: 520px;
  right: -140px;
  top: 40px;
  background: radial-gradient(circle, rgba(255, 214, 228, 0.6) 0%, rgba(255, 214, 228, 0) 72%);
  animation-delay: 3s;
}

.intro-gradient-c {
  width: 620px;
  height: 620px;
  left: 18%;
  bottom: -220px;
  background: radial-gradient(circle, rgba(205, 197, 255, 0.42) 0%, rgba(205, 197, 255, 0) 74%);
  animation-delay: 6s;
}

@keyframes floatBreath {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  50% {
    transform: translate3d(0, -10px, 0) scale(1.04);
  }
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
}
</style>
