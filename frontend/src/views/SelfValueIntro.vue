<template>
  <section class="intro-wrap">
    <div class="intro-card">
      <div class="intro-body">
        <p> "欢迎来到你的个人商业实验室。🧪</p>
        <p></p>
        <p> 在接下来的对话中，我们将一起完成一件重要的事：**把你的独特价值转化为可持续的商业系统**。</p>
        <p></p>
        <p> 这不是一次简单的问答，而是一次深度的自我考古。我会挑战你的假设，也会保护你的热情。</p>
        <p></p>
        <p> 准备好开始了吗？让我们从第一个问题出发：</p>
      </div>

      <div class="intro-actions">
        <!--
        <button class="intro-start-btn" type="button" @click="$emit('start')">
          确认开始
        </button>
        -->
        <button class="intro-start-btn" type="button" :disabled="starting" @click="handleStart">
          {{ starting ? '正在进入...' : '确认开始' }}
        </button>
      
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'SelfValueIntro',
  emits: ['start'],
  
  mounted() {
    this.$store.dispatch('prefetchFirstQuestion').catch(err => {
    console.error('预取第一题失败', err)
    })
  },

  methods: {
  async handleStart() {
    if (this.starting) return

    this.starting = true

    try {
      if (!this.$store.state.first_question_ready) {
        await this.$store.dispatch('prefetchFirstQuestion')
      }

      this.$emit('start')
    } catch (err) {
      console.error('进入问答失败', err)
    } finally {
      this.starting = false
    }
  }
}

}
</script>

<style scoped>
.intro-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--color-bg-page);
}

.intro-card {
  width: 100%;
  max-width: 820px;
  padding: 48px 40px;
  border-radius: 28px;
  background: rgba(255, 253, 249, 0.9);
  border: 1px solid rgba(216, 208, 197, 0.7);
  box-shadow: 0 10px 30px rgba(34, 28, 22, 0.06);
}

.intro-body p {
  margin: 0 0 14px;
  font-size: 18px;
  line-height: 1.9;
  color: rgba(47, 41, 36, 0.82);
  white-space: pre-wrap;
}

.intro-actions {
  margin-top: 28px;
}

.intro-start-btn {
  min-width: 140px;
  height: 46px;
  padding: 0 24px;
  border: none;
  border-radius: 999px;
  background: #2f4f6f;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 8px 20px rgba(47, 79, 111, 0.18);
}

.intro-start-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(47, 79, 111, 0.22);
}

@media (max-width: 768px) {
  .intro-card {
    padding: 32px 22px;
    border-radius: 22px;
  }

  .intro-body p {
    font-size: 16px;
    line-height: 1.8;
  }

  .intro-start-btn {
    width: 100%;
  }
}
</style>
