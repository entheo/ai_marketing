<template>
  <div class="home-page" :class="{ 'home-page--modal-open': showLoginModal || showRegisterModal }">
    <PrismFlowBackground
      class="home-flow"
      :pause-interaction="showLoginModal || showRegisterModal"
      :pause-animation="showLoginModal || showRegisterModal"
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
            @click="handleEnterLab"
          >
            进入实验室
          </button>
        </div>
      </section>
    </main>

    <!-- 登录遮罩 -->
    <transition name="fade">
      <div
        v-if="showLoginModal"
        class="login-modal-overlay"
        @click="closeLoginModal"
      ></div>
    </transition>

    <!-- 登录浮层 -->
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
                placeholder="请输入用户名"
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

    <!-- 注册遮罩 -->
    <transition name="fade">
      <div
        v-if="showRegisterModal"
        class="login-modal-overlay"
        @click="closeRegisterModal"
      ></div>
    </transition>

    <!-- 注册浮层 -->
    <transition name="modal-rise">
      <div v-if="showRegisterModal" class="login-modal-wrap">
        <div class="login-modal" @click.stop>
          <button class="login-close" type="button" @click="closeRegisterModal">
            ×
          </button>

          <div class="login-brand">注册账户</div>
          <p class="login-subtitle">
            输入邀请码，开始进入实验室。
          </p>

          <form class="login-form" @submit.prevent="handleRegister">
            <div class="login-field">
              <label class="login-label">用户名</label>
              <input
                v-model="registerForm.username"
                class="login-input"
                type="text"
                placeholder="请输入用户名"
              />
            </div>

            <div class="login-field">
              <label class="login-label">密码</label>
              <input
                v-model="registerForm.password"
                class="login-input"
                type="password"
                placeholder="请输入密码"
              />
            </div>

            <div class="login-field">
              <label class="login-label">邀请码</label>
              <input
                v-model="registerForm.invitation_code"
                class="login-input"
                type="text"
                placeholder="请输入邀请码"
              />
            </div>

            <div v-if="registerError" class="login-error">
              {{ registerError }}
            </div>

            <div v-if="registerSuccess" class="login-success">
              {{ registerSuccess }}
            </div>

            <button class="login-submit" type="submit">
              注册
            </button>
          </form>

          <div class="login-footer">
            已有账户？
            <button class="login-link" type="button" @click="goLogin">
              返回登录
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
      showRegisterModal: false,

      loginError: '',
      registerError: '',
      registerSuccess: '',

      loginForm: {
        username: '',
        password: ''
      },

      registerForm: {
        username: '',
        password: '',
        invitation_code: ''
      }
    }
  },
mounted() {
  if (this.$route.query.loginRequired === '1') {
    this.loginError = '请先登录后进入实验室'
    this.showLoginModal = true
    this.loginError = '请先登录后再进入实验室'
  }
},
methods: {
  
  openLoginModal() {
    this.showRegisterModal = false
    this.showLoginModal = true
    this.loginError = ''
  },

  closeLoginModal() {
    this.showLoginModal = false
    this.loginError = ''
  },

  closeRegisterModal() {
    this.showRegisterModal = false
    this.registerError = ''
    this.registerSuccess = ''
  },

  goRegister() {
    this.showLoginModal = false
    this.loginError = ''
    this.showRegisterModal = true
  },

  goLogin() {
    this.showRegisterModal = false
    this.registerError = ''
    this.registerSuccess = ''
    this.showLoginModal = true
  },

  handleEnterLab(){
      if (this.$store.getters.isLoggedIn){
          this.$router.push('/dashboard')
          } else{
              this.openLoginModal()
              }
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
  },

  async handleRegister() {
    this.registerError = ''
    this.registerSuccess = ''

    if (
      !this.registerForm.username ||
      !this.registerForm.password ||
      !this.registerForm.invitation_code
    ) {
      this.registerError = '请填写完整信息'
      return
    }

    try {
      const registeredUsername = this.registerForm.username

      await this.$store.dispatch('register', {
        username: registeredUsername,
        password: this.registerForm.password,
        invitation_code: this.registerForm.invitation_code
      })

      this.registerForm = {
        username: '',
        password: '',
        invitation_code: ''
      }

      this.showRegisterModal = false
      this.registerError = ''
      this.registerSuccess = ''

      this.loginForm.username = registeredUsername
      this.loginForm.password = ''
      this.loginError = '注册成功，请重新输入密码后登录'
      this.showLoginModal = true
    } catch (error) {
      const data = error?.response?.data

      if (typeof data === 'object' && data !== null) {
        this.registerError =
          data.invitation_code?.[0] ||
          data.username?.[0] ||
          data.password?.[0] ||
          '注册失败'
      } else {
        this.registerError = '注册失败'
      }
    }
  }
}
  /*
  methods: {
    openLoginModal() {
      this.showRegisterModal = false
      this.showLoginModal = true
      this.loginError = ''
    },

    closeLoginModal() {
      this.showLoginModal = false
      this.loginError = ''
    },

    closeRegisterModal() {
      this.showRegisterModal = false
      this.registerError = ''
      this.registerSuccess = ''
    },

    goRegister() {
      this.showLoginModal = false
      this.loginError = ''
      this.showRegisterModal = true
    },

    goLogin() {
      this.showRegisterModal = false
      this.registerError = ''
      this.registerSuccess = ''
      this.showLoginModal = true
    },


    async handleRegister() {
      this.registerError = ''
      this.registerSuccess = ''

  if (
    !this.registerForm.username ||
    !this.registerForm.password ||
    !this.registerForm.invitation_code
  ) {
    this.registerError = '请填写完整信息'
    return
  }

  try {
    const registeredUsername = this.registerForm.username
    //const registeredPassword = this.registerForm.password

    await this.$store.dispatch('register', {
      username: registeredUsername,
      password: this.registerForm.password,
      invitation_code: this.registerForm.invitation_code
    })

    this.registerForm = {
      username: '',
      password: '',
      invitation_code: ''
    }

    this.showRegisterModal = false
    this.registerError = ''
    this.registerSuccess = ''

    this.loginForm.username = registeredUsername
    this.loginForm.password = ''
    this.loginError = '注册成功，请重新输入密码登录'
    this.showLoginModal = true
  } catch (error) {
    const data = error?.response?.data

    if (typeof data === 'object' && data !== null) {
      this.registerError =
        data.invitation_code?.[0] ||
        data.username?.[0] ||
        data.password?.[0] ||
        '注册失败'
    } else {
      this.registerError = '注册失败'
    }
  }
}
  }

*/
}
</script>

<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: #f8f4ef;
}

.home-page--modal-open {
  overflow: hidden;
}

.home-flow {
  position: absolute;
  inset: 0;
  z-index: 0;
  filter: none;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 18px;
  font-size: 52px;
  line-height: 1.5;
  letter-spacing: 0.01em;
  color: #2a2824;
  font-weight: 600;
}

.brand-mark {
  display: inline-flex;
  width: 60px;
  height: 60px;
  flex: 0 0 60px;
  color: #2a2824;
  opacity: 0.92;
}

.brand-mark svg {
  width: 100%;
  height: 100%;
  display: block;
}

.brand-text {
  display: inline-block;
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

.login-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 20;
  background: rgba(38, 34, 30, 0.18);
  backdrop-filter: blur(6px);
}

.login-modal-wrap {
  position: fixed;
  inset: 0;
  z-index: 21;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  border-radius: 28px;
  padding: 34px 28px 28px;
  background: rgba(255, 252, 248, 0.94);
  box-shadow:
    0 22px 60px rgba(55, 47, 40, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(120, 110, 98, 0.08);
}

.login-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 999px;
  background: rgba(90, 83, 76, 0.08);
  color: #514a44;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.login-close:hover {
  background: rgba(90, 83, 76, 0.14);
}

.login-brand {
  font-size: 24px;
  line-height: 1.3;
  font-weight: 600;
  color: #2b2622;
  text-align: center;
}

.login-subtitle {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: rgba(58, 51, 45, 0.76);
  text-align: center;
}

.login-form {
  margin-top: 24px;
}

.login-field + .login-field {
  margin-top: 16px;
}

.login-label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #4a433d;
}

.login-input {
  width: 100%;
  height: 48px;
  border: 1px solid rgba(112, 100, 88, 0.14);
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.82);
  color: #2d2824;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.login-input:focus {
  border-color: rgba(77, 89, 101, 0.4);
  box-shadow: 0 0 0 4px rgba(77, 89, 101, 0.08);
  background: #fff;
}

.login-error {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #a64b44;
}

.login-success {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #2f6b57;
}

.login-submit {
  width: 100%;
  margin-top: 18px;
  height: 48px;
  border: none;
  border-radius: 999px;
  background: rgba(77, 89, 101, 0.92);
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 12px 28px rgba(62, 71, 80, 0.14);
  transition: transform 0.18s ease, background 0.18s ease;
}

.login-submit:hover {
  transform: translateY(-1px);
  background: rgba(68, 79, 90, 0.96);
}

.login-footer {
  margin-top: 18px;
  text-align: center;
  font-size: 14px;
  color: #5a524b;
}

.login-link {
  margin-left: 6px;
  padding: 0;
  border: none;
  background: transparent;
  color: #465461;
  font-size: 14px;
  cursor: pointer;
}

.login-link:hover {
  text-decoration: underline;
}

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
  transition: all 0.24s ease;
}

.modal-rise-enter-from,
.modal-rise-leave-to {
  opacity: 0;
  transform: translateY(14px);
}

@media (max-width: 768px) {
  .hero-shell {
    padding: 32px 20px 48px;
  }

  .brand-line {
    gap: 10px;
    font-size: 28px;
    line-height: 1.4;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .brand-mark {
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
  }

  .hero-title {
    font-size: 22px;
    line-height: 1.6;
  }

  .hero-actions {
    margin-top: 42px;
  }

  .hero-btn {
    width: 100%;
    max-width: 280px;
  }

  .login-modal-wrap {
    padding: 16px;
  }

  .login-modal {
    max-width: none;
    padding: 28px 20px 22px;
    border-radius: 22px;
  }
}
</style>
