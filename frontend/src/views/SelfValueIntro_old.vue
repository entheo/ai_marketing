<template>
  <section class="intro-wrap">
    <div class="intro-softener"></div>
    <div class="intro-center-glow"></div>

    <div class="intro-shell">
      <section class="intro-card">
        <div class="intro-mark" aria-hidden="true">
          <svg
            viewBox="0 0 100 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g
              stroke="currentColor"
              stroke-width="3.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M50 12 L28 72" />
              <path d="M50 12 L72 72" />
              <path d="M28 72 L50 84" />
              <path d="M50 84 L72 72" />
              <path d="M28 72 L50 58" />
              <path d="M50 58 L72 72" />
              <path d="M50 12 L50 58" />
              <path d="M50 58 L48 84" />
            </g>
          </svg>
        </div>

        <div class="intro-body">
          <p class="intro-paragraph intro-paragraph--lead">
            欢迎来到属于你的【个人商业实验室】
          </p>

          <p class="intro-paragraph">
            在接下来的对话中，我们将一起完成一件重要的事：<br>
            <span class="intro-strong">把你的独特价值转化为可持续的商业系统</span>。
          </p>

          <p class="intro-paragraph">
            这不是一次简单的对话，而是一次深度的自我考古。<br>
            <span class="intro-strong">我会挑战你的假设，也会保护你的热情。</span>
          </p>

          <p class="intro-paragraph intro-paragraph--ending">
            准备好开始了吗？让我们从第一个问题出发：
          </p>
        </div>

        <div class="intro-actions">
          <button
            class="hero-btn hero-btn--primary"
            type="button"
            :disabled="starting || firstQuestionLoading"
            @click="handleStart"
          >
            {{ buttonText }}
          </button>
        </div>
      </section>
    </div>
  </section>
</template>
<script>
export default {
  name: 'SelfValueIntro',
  emits: ['start'],

  data() {
    return {
      starting: false
    }
  },

  computed: {
    firstQuestionLoading() {
      return this.$store.state.first_question_loading
    },
    buttonText() {
      return (this.starting || this.firstQuestionLoading) ? '正在准备...' : '好的，开始！'
    }
  },

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
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #f8f4ef;
}

.intro-softener {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 18% 20%, rgba(255, 255, 255, 0.62), transparent 36%),
    radial-gradient(circle at 82% 78%, rgba(255, 250, 245, 0.5), transparent 40%),
    radial-gradient(circle at 50% 46%, rgba(255, 253, 249, 0.36), transparent 46%),
    linear-gradient(
      180deg,
      rgba(252, 248, 243, 0.78) 0%,
      rgba(250, 246, 241, 0.68) 38%,
      rgba(249, 245, 240, 0.72) 100%
    );
}

.intro-center-glow {
  position: absolute;
  left: 50%;
  top: 46%;
  width: 680px;
  height: 320px;
  transform: translate(-50%, -50%);
  z-index: 1;
  pointer-events: none;
  border-radius: 999px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 254, 251, 0.42) 0%,
    rgba(255, 251, 247, 0.16) 42%,
    rgba(255, 248, 242, 0) 76%
  );
  filter: blur(42px);
}

.intro-shell {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px 56px;
}

.intro-card {
  width: 100%;
  max-width: 920px;
  padding: 42px 38px 34px;
  border-radius: 28px;
  background: rgba(255, 252, 248, 0.68);
  box-shadow:
    0 22px 60px rgba(55, 47, 40, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.52);
  border: 1px solid rgba(120, 110, 98, 0.06);
  backdrop-filter: blur(6px);
}

.intro-mark {
  width: 34px;
  height: 34px;
  margin: 0 auto 28px;
  color: #2a2824;
  opacity: 0.9;
}

.intro-mark svg {
  width: 100%;
  height: 100%;
  display: block;
}

.intro-body {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.intro-paragraph {
  margin: 0;
  font-size: 18px;
  line-height: 2;
  letter-spacing: -0.01em;
  font-weight: 420;
  color: #2e2824;
}

.intro-paragraph + .intro-paragraph {
  margin-top: 24px;
}

.intro-paragraph--lead {
  font-size: 34px;
  line-height: 1.85;
  color: #2a2824;
}

.intro-strong {
  font-weight: 600;
  color: #26211d;
}

.intro-paragraph--ending {
  margin-top: 30px;
  color: #3a332d;
}

.intro-actions {
  display: flex;
  justify-content: center;
  margin-top: 38px;
}

.hero-btn {
  appearance: none;
  border-radius: 999px;
  padding: 16px 34px;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    opacity 0.18s ease;
}

.hero-btn:hover {
  transform: translateY(-1px);
}

.hero-btn--primary {
  border: none;
  background: rgba(77, 89, 101, 0.92);
  color: #fff;
  box-shadow: 0 12px 28px rgba(62, 71, 80, 0.14);
}

.hero-btn--primary:hover {
  background: rgba(68, 79, 90, 0.96);
}

.hero-btn--primary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
  transform: none;
  background: rgba(77, 89, 101, 0.78);
  box-shadow: 0 8px 18px rgba(62, 71, 80, 0.1);
}

@media (max-width: 768px) {
  .intro-shell {
    padding: 28px 16px 28px;
  }

  .intro-card {
    padding: 28px 20px 22px;
    border-radius: 22px;
  }

  .intro-mark {
    width: 28px;
    height: 28px;
    margin-bottom: 22px;
  }

  .intro-body {
    max-width: none;
  }

  .intro-paragraph {
    font-size: 16px;
    line-height: 1.9;
  }

  .intro-paragraph + .intro-paragraph {
    margin-top: 18px;
  }

  .intro-paragraph--lead {
    font-size: 18px;
    line-height: 1.8;
  }

  .intro-paragraph--ending {
    margin-top: 22px;
  }

  .intro-actions {
    margin-top: 28px;
  }

  .hero-btn {
    width: 100%;
    max-width: 280px;
  }
}
</style>
