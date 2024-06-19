// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';

// 引入你的Vue组件
import HomePage from '../components/HomePage.vue';
import Dashboard from '../components/Dashboard.vue';
import LoginPage from '../components/LoginPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    // 这个meta字段可以用来检查用户是否登录
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

export default router;
