<template>
  <div class="self-value-landing">
    <div class="landing-container">
      <div class="landing-eyebrow">自我价值梳理</div>

      <h1 class="landing-title">
        也许你不是突然迷失了，而是过去那套支撑你的身份，正在失去力量。
      </h1>

      <p class="landing-subtitle">
        通过一组问题与专属报告，帮你整理那些正在松动的部分，并重新看见你的价值线索。
      </p>

      <button class="landing-button" type="button" @click="goIntro">
        开始这次梳理
      </button>
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
.self-value-landing {
  min-height: 100vh;
  background: #f7f4ef;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  box-sizing: border-box;
}

.landing-container {
  width: 100%;
  max-width: 760px;
  color: #1f1f1f;
}

.landing-eyebrow {
  font-size: 14px;
  line-height: 1.6;
  color: #7a746b;
  letter-spacing: 0.08em;
  margin-bottom: 20px;
}

.landing-title {
  font-size: 40px;
  line-height: 1.4;
  font-weight: 600;
  margin: 0 0 24px;
  color: #1b1a18;
}

.landing-subtitle {
  font-size: 18px;
  line-height: 1.9;
  color: #4d4740;
  margin: 0 0 36px;
  max-width: 640px;
}

.landing-button {
  border: none;
  background: #2f2a24;
  color: #ffffff;
  font-size: 16px;
  line-height: 1;
  padding: 15px 28px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.landing-button:hover {
  background: #1f1b17;
}

@media (max-width: 768px) {
  .landing-title {
    font-size: 30px;
    line-height: 1.5;
  }

  .landing-subtitle {
    font-size: 16px;
    line-height: 1.8;
  }

  .landing-button {
    width: 100%;
  }
}
</style>
