<template>
  <div class="dashboard-root">
    <aside class="dashboard-rail">
      <div class="rail-top">
        <button class="rail-toggle" type="button" @click="menuOpen = true">
          ☰
        </button>
      </div>
    </aside>

    <main class="dashboard-main">
      <router-view />
    </main>

    <transition name="drawer-fade">
      <div
        v-if="menuOpen"
        class="dashboard-overlay"
        @click="menuOpen = false"
      ></div>
    </transition>

    <transition name="drawer-slide">
      <aside v-if="menuOpen" class="dashboard-drawer">
        <div class="drawer-head">
          <button
            class="drawer-brand-mark"
            type="button"
            @click="goHome"
            title="返回首页"
          >
            棱镜
          </button>

          <div class="drawer-brand-slogan">看清自己，让价值落地</div>

          <button class="drawer-close" type="button" @click="menuOpen = false">
            ×
          </button>
        </div>

        <div v-if="$store.getters.isLoggedIn" class="drawer-account-line">
          <div class="drawer-account-name">
            你好，{{ displayUsername }}
          </div>

          <button class="drawer-inline-link" type="button" @click="handleLogout">
            退出
          </button>
        </div>

        <div v-else class="drawer-account-line">
          <div class="drawer-account-name">未登录</div>
        </div>

        <div class="drawer-nav-list">
          <button
            class="drawer-nav"
            :class="{ 'drawer-nav--active': isActive('/dashboard/questions') }"
            type="button"
            @click="openAndGo('/dashboard/questions')"
          >
            认识自己
          </button>

          <button
            class="drawer-nav"
            :class="{ 'drawer-nav--active': isActive('/dashboard/canvas') }"
            type="button"
            @click="openAndGo('/dashboard/canvas')"
          >
            梳理路径
          </button>
        </div>

        <div class="drawer-divider"></div>

        <div class="drawer-nav-list drawer-nav-list--secondary">
          <button
            class="drawer-nav drawer-nav--secondary"
            :class="{ 'drawer-nav--active': isActive('/dashboard/market') }"
            type="button"
            @click="openAndGo('/dashboard/market')"
          >
            观察市场
          </button>

          <button
            class="drawer-nav drawer-nav--secondary"
            :class="{ 'drawer-nav--active': isActive('/dashboard/rednote') }"
            type="button"
            @click="openAndGo('/dashboard/rednote')"
          >
            评估名字
          </button>
        </div>

        <div class="drawer-bottom-link">
          <button class="drawer-inline-link" type="button" @click="showContactModal = true">
            联系作者
          </button>
        </div>
      </aside>
    </transition>

    <n-modal
      v-model:show="showContactModal"
      preset="card"
      style="width: 420px;"
      title="联系作者"
    >
      <div class="contact-content">
        如果你想反馈问题、交流想法，或者聊聊你正在做的方向，可以在这里放你的联系方式。
      </div>
    </n-modal>
  </div>
</template>

<script>
import { NModal } from 'naive-ui'

export default {
  name: 'DashboardPage',

  components: {
    NModal
  },

  data() {
    return {
      menuOpen: false,
      showContactModal: false
    }
  },

  computed: {
    displayUsername() {
      return this.$store.state.user || ''
    }
  },

  methods: {
    openAndGo(path) {
      this.menuOpen = false
      this.$router.push(path)
    },

    isActive(path) {
      return this.$route.path === path
    },

    goHome() {
      this.menuOpen = false
      this.$router.push('/')
    },

    async handleLogout() {
      try {
        await this.$store.dispatch('logout')
        this.menuOpen = false
        window.location.href = '/'
      } catch (error) {
        console.error('退出登录失败', error)
      }
    }
  }
}
</script>

<style scoped>
.dashboard-root {
  position: relative;
  min-height: 100vh;
  background: var(--color-bg-page);
}

.dashboard-rail {
  position: fixed;
  left: 18px;
  top: 18px;
  width: auto;
  background: transparent;
  border: none;
  z-index: 20;
}

.rail-top {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.rail-toggle {
  width: 42px;
  height: 40px;
  border: none;
  border-radius: 14px;
  cursor: pointer;
  background: rgba(255, 253, 249, 0.24);
  color: rgba(31, 28, 23, 0.72);
  font-size: 17px;
  line-height: 1;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 14px rgba(34, 28, 22, 0.03);
  transition: background 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}

.rail-toggle:hover {
  background: rgba(255, 253, 249, 0.5);
  color: rgba(31, 28, 23, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(34, 28, 22, 0.05);
}

.dashboard-main {
  margin-left: 0;
  min-height: 100vh;
  background: var(--color-bg-page);
}

.dashboard-overlay {
  position: fixed;
  inset: 0;
  background: rgba(24, 20, 16, 0.16);
  z-index: 39;
}

.dashboard-drawer {
  position: fixed;
  left: 72px;
  top: 0;
  bottom: 0;
  width: 280px;
  background: #fffdf9;
  border-right: 1px solid rgba(216, 208, 197, 0.7);
  box-shadow: 8px 0 30px rgba(34, 28, 22, 0.08);
  z-index: 40;
  display: flex;
  flex-direction: column;
  padding: 18px 16px 16px;
}

.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.drawer-brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  border: none;
  background: #f3ede5;
  color: var(--color-text-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  flex-shrink: 0;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.18s ease;
}

.drawer-brand-mark:hover {
  background: #eee5d8;
  transform: translateY(-1px);
}

.drawer-close {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.drawer-close:hover {
  background: rgba(93, 83, 72, 0.08);
  color: var(--color-text-strong);
}

.drawer-account-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 30px 0 14px;
  padding: 2px 4px 10px;
}

.drawer-account-name {
  flex: 1;
  min-width: 0;
  display:block;
  text-align:left;
  font-size: 13px;
  font-weight: 500;
  color: rgba(47, 41, 36, 0.84);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.drawer-brand-block {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.drawer-brand-slogan {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(88, 78, 69, 0.72);
  white-space: nowrap;
}
.drawer-inline-link {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 13px;
  color: rgba(88, 78, 69, 0.72);
  cursor: pointer;
  transition: color 0.18s ease;
}

.drawer-inline-link:hover {
  color: var(--color-text-strong);
}

.drawer-nav-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.drawer-nav-list--secondary {
  gap: 4px;
}

.drawer-divider {
  height: 1px;
  margin: 14px 4px 12px;
  background: rgba(218, 209, 198, 0.58);
}

.drawer-nav {
  position: relative;
  width: 100%;
  display: block;
  text-align: left;
  padding: 12px 14px;
  border: none;
  border-radius: 14px;
  background: transparent;
  color: var(--color-text-strong);
  font-size: 15px;
  line-height: 1.45;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.18s ease, color 0.18s ease;
}

.drawer-nav:hover {
  background: #f6f1ea;
  transform: translateY(-1px);
}

.drawer-nav--secondary {
  font-size: 14px;
  color: rgba(59, 52, 46, 0.76);
}

.drawer-nav--secondary:hover {
  background: rgba(246, 241, 234, 0.72);
}

.drawer-nav--active {
  background: #f5efe7;
  color: var(--color-text-strong);
  font-weight: 600;
}

.drawer-bottom-link {
  margin-top: auto;
  padding: 10px 4px 2px;
  border-top: 1px solid rgba(214, 205, 194, 0.42);
}

.contact-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-text-muted);
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.18s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.22s ease, opacity 0.22s ease;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-14px);
  opacity: 0;
}

@media (max-width: 768px) {
  .dashboard-drawer {
    left: 0;
    width: min(82vw, 300px);
  }
}
</style>
