// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
//import { useStore } from 'vuex';
import store from '@/store';  // 从 '@/store' 导入 Vuex store

// 引入你的Vue组件
import HomePage from '../components/HomePage.vue';
import DashboardPage from '../components/DashboardPage.vue';
//import TestDashboardPage from '../components/TestDashboardPage.vue';
import LoginPage from '../components/LoginPage.vue';
import OldCampaignPage from '../components/OldCampaignPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
      path: '/dashboard',
      name: 'Dashboard',
      component: DashboardPage,
    // 这个meta字段可以用来检查用户是否登录
       meta: { requiresAuth: true }
  },
  {   path: '/campaign',
      name: 'Campaign',
      component:OldCampaignPage,
       meta: { requiresAuth: true }
      },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 应用启动时从localStorage恢复状态
//const restoreAuthState = () => {
//  const authStore = useStore();
//  console.log(authStore.getters.isLogedIn);
//  const token = localStorage.getItem('user'); // 假设存储的令牌键名为'authToken'
//  console.log(token)
//  if (token) {
//    authStore.logIn(token);
//  }
// };
///

const restoreAuthState = () => {
  //console.log(localStorage);
  if (localStorage.getItem('token')) {
    // 这里是假设存储的令牌键名为 'token'
    const token = localStorage.getItem('token');
    const user = {}; // 这里需要从某处获取或初始化 user 信息
    store.commit('auth_success', { token, user });
  }
};


router.beforeEach((to, from, next) => {
  restoreAuthState(); 
  if (to.matched.some(record => record.meta.requiresAuth) && !store.getters.isLoggedIn) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
