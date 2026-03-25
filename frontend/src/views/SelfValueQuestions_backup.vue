<template>
  <div class="self-value-questions">
    <div class="questions-container">
      <div class="questions-eyebrow">问题页</div>

      <h1 class="questions-title">
        这里将进入正式问题流程。
      </h1>

      <p class="questions-subtitle">
        这一页先作为占位，下一步我们再一起决定问题结构与呈现方式。
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelfValueQuestions'
}
</script>

<style scoped>
.self-value-questions {
  min-height: 100vh;
  background: #fcfaf7;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  box-sizing: border-box;
}

.questions-container {
  width: 100%;
  max-width: 760px;
  color: #1f1f1f;
}

.questions-eyebrow {
  font-size: 14px;
  line-height: 1.6;
  color: #7a746b;
  letter-spacing: 0.08em;
  margin-bottom: 20px;
}

.questions-title {
  font-size: 36px;
  line-height: 1.45;
  font-weight: 600;
  margin: 0 0 20px;
  color: #1b1a18;
}

.questions-subtitle {
  font-size: 18px;
  line-height: 1.9;
  color: #4d4740;
  margin: 0;
  max-width: 640px;
}

@media (max-width: 768px) {
  .questions-title {
    font-size: 28px;
    line-height: 1.5;
  }

  .questions-subtitle {
    font-size: 16px;
    line-height: 1.8;
  }
}
</style>
