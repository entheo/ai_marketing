<template>
  <div class="home-page" :class="{'home-page--modal-open':showLoginModal}">
    <PrismFlowBackground
      class="home-flow"
      :pause-interaction="showLoginModal"
      :pause-animation = "showLoginModal"
    />
    <div class="home-flow-softener"></div>
    <div class="home-flow-center-glow"></div>

    <main class="hero-shell">
    <section class="hero">
      <div class="brand-line">
      <span class="brand-mark" aria-hidden="true">
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
      </span>

      <span class="brand-text">棱镜｜个人商业实验室</span>
    </div>

    <p class="hero-title">
      也许你不是没有价值，只是一直没有被真正看见。
    </p>

    <div class="hero-actions">
      <button
        class="hero-btn hero-btn--primary"
        type="button"
        @click="showLoginModal = true"
      >
        进入实验室
      </button>
    </div>
  </section>
    </main>

    <transition name="fade">
      <div
        v-if="showLoginModal"
        class="login-modal-overlay"
        @click="closeLoginModal"
      ></div>
    </transition>

    <transition name="modal-rise">
      <div v-if="showLoginModal" class="login-modal-wrap">
        <div class="login-modal" @click.stop>
          <button class="login-close" type="button" @click="closeLoginModal">
            ×
          </button>

          <div class="login-brand">进入实验室</div>
          <p class="login-subtitle">
            从这里开始，重新看见自己。
          </p>

          <form class="login-form" @submit.prevent="handleLogin">
            <div class="login-field">
              <label class="login-label">账号</label>
              <input
                v-model="loginForm.username"
                class="login-input"
                type="text"
                placeholder="请输入用户名或邮箱"
              />
            </div>

            <div class="login-field">
              <label class="login-label">密码</label>
              <input
                v-model="loginForm.password"
                class="login-input"
                type="password"
                placeholder="请输入密码"
              />
            </div>

            <div v-if="loginError" class="login-error">
              {{ loginError }}
            </div>

            <button class="login-submit" type="submit">
              登录并进入
            </button>
          </form>

          <div class="login-footer">
            还没有账户？
            <button class="login-link" type="button" @click="goRegister">
              立即注册
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import PrismFlowBackground from '../components/PrismFlowBackground.vue'

export default {
  name: 'HomePage',
  components: {
    PrismFlowBackground
  },
  data() {
    return {
      showLoginModal: false,
      loginError: '',
      loginForm: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    closeLoginModal() {
      this.showLoginModal = false
      this.loginError = ''
    },

    goRegister() {
      this.$router.push('/register')
    },

    async handleLogin() {
      this.loginError = ''

      if (!this.loginForm.username || !this.loginForm.password) {
        this.loginError = '请输入账号和密码'
        return
      }

      try {
        await this.$store.dispatch('logIn', {
          username: this.loginForm.username,
          password: this.loginForm.password,
          keep_logged_in_for_days: 7
        })

        this.showLoginModal = false
        this.$router.push('/dashboard')
      } catch (error) {
        this.loginError = error?.response?.data?.message || '账号或密码错误'
      }
    }
  }
}
</script>
<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #f8f4ef;
}

.home-flow {
  position: absolute;
  inset: 0;
  z-index: 0;
  filter: /* saturate(0.5) brightness(1.34) contrast(0.78) */ none;
  opacity: 0.74;
}

.home-flow-softener {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background:
   radial-gradient(circle at 18% 20%, rgba(255, 255, 255, 0.68), transparent 36%),
   radial-gradient(circle at 82% 78%, rgba(255, 250, 245, 0.56), transparent 40%),
    radial-gradient(circle at 50% 46%, rgba(255, 253, 249, 0.42), transparent 46%),
    linear-gradient(
      180deg,
      rgba(252, 248, 243, 0.76) 0%,
      rgba(250, 246, 241, 0.62) 38%,
      rgba(249, 245, 240, 0.66) 100%
    );
  backdrop-filter: none;
}

.home-flow-center-glow {
  position: absolute;
  left: 50%;
  top: 48%;
  width: 640px;
  height: 300px;
  transform: translate(-50%, -50%);
  z-index: 2;
  pointer-events: none;
  border-radius: 999px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 254, 251, 0.46) 0%,
    rgba(255, 251, 247, 0.18) 42%,
    rgba(255, 248, 242, 0) 76%
  );
  filter: blur(42px);
}

.hero-shell {
  position: relative;
  z-index: 3;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px 56px;
}

.hero {
  width: 100%;
  max-width: 760px;
  text-align: center;
}

.brand-line {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:12px;
  margin-bottom: 18px;
  font-size: 52px;
  line-height: 1.5;
  letter-spacing: 0.01em;
  color: #2a2824;
  font-weight: 600;
}

.brand-mark{
    display:inline-flex;
    width:60px;
    height:60px;
    flex:0 0 60px;
    color:#2a2824;
    opacity:0.92;
    }
.brand-mark svg {
    width:100%;
    height:100%;
    display:block;
    }
.brand-text{
    display:inline-block;
    }
.hero-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.58;
  letter-spacing: -0.012em;
  font-weight: 420;
  color: #2e2824;
  text-wrap: balance;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 68px;
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
    color 0.18s ease;
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

/* 浮层 */
.login-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10;
  background: 
    linear-gradient(
    180deg,
    rgba(44,36,30,0.18) 0%,
    rgba(44, 36, 30, 0.12) 100%
    );
  backdrop-filter: none /* blur(4px) */;
}

.login-modal-wrap {
  position: fixed;
  inset: 0;
  z-index: 11;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  poiter-events:none;
}

.login-modal {
  position: relative;
  width: 100%;
  max-width: 380px;
  border: 1px solid rgba(206, 196, 183, 0.72);
  border-radius: 22px;
  background: #fdfaf6;
  box-shadow:
    0 18px 48px rgba(54, 45, 33, 0.10),
    0 4px 12px rgba(54,45,33,0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
  backdrop-filter: /* blur(12px) */ none;
  padding: 22px 18px 18px;
  pointer-events:auto;
  }


.login-modal::before {
  content: '';
  position: absolute;
  left: 14px;
  right: 14px;
  top: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.72);
  pointer-events: none;
}
.login-close {
  position: absolute;
  right: 10px;
  top: 8px;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #857d72;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.login-brand {
  font-size: 20px;
  line-height: 1.45;
  color: #2a2824;
  font-weight: 600;
  text-align: center;
}

.login-subtitle {
  margin: 6px 0 18px;
  font-size: 13px;
  line-height: 1.8;
  color: #8a8276;
  text-align: center;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-label {
  font-size: 13px;
  line-height: 1.6;
  color: #6f675c;
}

.login-input {
  width: 100%;
  border: 1px solid rgba(198, 190, 178, 0.62);
  border-radius: 14px;
  background: rgba(255, 253, 250, 0.96);
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.5;
  color: #2e2824;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.login-input:focus {
  border-color: rgba(157, 146, 132, 0.88);
  box-shadow: 0 0 0 3px rgba(214, 205, 193, 0.24);
}

.login-error {
  font-size: 13px;
  line-height: 1.7;
  color: #b42318;
}

.login-submit {
  margin-top: 2px;
  border: none;
  border-radius: 999px;
  background: rgba(77, 89, 101, 0.94);
  color: #fff;
  padding: 13px 18px;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.18s ease;
}

.login-submit:hover {
  background: rgba(68, 79, 90, 0.98);
  transform: translateY(-1px);
}

.login-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  line-height: 1.8;
  color: #847c71;
}

.login-link {
  border: none;
  background: transparent;
  color: #4d5965;
  font-size: 13px;
  line-height: 1.8;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
}

.login-link:hover {
  text-decoration: underline;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.22s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-rise-enter-active,
.modal-rise-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.modal-rise-enter-from,
.modal-rise-leave-to {
  opacity: 0;
  transform: translateY(10px);
}


.home-page--modal-open .home-flow-center-glow {
  opacity: 0.32;
}

.home-page--modal-open .home-flow-softener{
    opacity:0.9
    }
    

@media (max-width: 900px) {
  .brand-line {
    font-size: 38px;
  }

  .hero-title {
    font-size: 24px;
    line-height: 1.54;
  }

  .home-flow-center-glow {
    width: 860px;
    height: 500px;
  }
}

@media (max-width: 768px) {
  .hero-shell {
    align-items: flex-start;
    padding: 44px 18px 40px;
  }

  .brand-line {
    gap:9px;
    font-size: 32px;
    line-height: 1.4;
  }
  .brand-mark{
      width:28px;
      heigh:28px;
      flex:0 0 28px;
      }
  .hero-title {
    font-size: 24px;
    line-height: 1.6;
  }

  .hero-actions {
    margin-top: 52px;
  }

  .hero-btn {
    width: 100%;
  }

  .home-flow-center-glow {
    width: 620px;
    height: 380px;
  }

  .login-modal {
    border-radius: 20px;
    padding: 20px 16px 16px;
  }
}
</style>
