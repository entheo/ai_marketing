import { createRouter, createWebHistory } from 'vue-router';
import SelfValueLanding from '../views/SelfValueLanding.vue';
import SelfValueIntro from '../views/SelfValueIntro.vue';
import SelfValueQuestions from '../views/SelfValueQuestions.vue';
import SelfValueReport from '../views/SelfValueReport.vue';
import store from '@/store';

import HomePage from '../views/HomePage.vue';
import DashboardPage from '../views/DashboardPage.vue';
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
    component: DashboardPage,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard/questions'
      },
      {
        path: 'questions',
        name: 'DashboardQuestions',
        component: SelfValueQuestions
      },
      {
        path: 'canvas',
        name: 'DashboardCanvas',
        component: {
          template: `
            <div class="page-shell">
              <div class="page-container">
                <div class="ui-eyebrow">个人商业画布</div>
                <h1 class="ui-title">这里将承接个人商业画布</h1>
                <p class="ui-subtitle">后面我们再把你的优势、方向、验证路径和行动步骤收进这里。</p>
              </div>
            </div>
          `
        }
      },
      {
        path: 'market',
        name: 'DashboardMarket',
        component: {
          template: `
            <div class="page-shell">
              <div class="page-container">
                <div class="ui-eyebrow">分账分析，解读市场</div>
                <h1 class="ui-title">这里将承接市场分析功能</h1>
                <p class="ui-subtitle">后面可以继续接旧项目里的市场分析能力。</p>
              </div>
            </div>
          `
        }
      },
      {
        path: 'rednote',
        name: 'DashboardRednote',
        component: {
          template: `
            <div class="page-shell">
              <div class="page-container">
                <div class="ui-eyebrow">小红书账号评分</div>
                <h1 class="ui-title">这里将承接小红书账号评分</h1>
                <p class="ui-subtitle">后面可以继续接旧项目里的小红书评分能力。</p>
              </div>
            </div>
          `
        }
      }
    ]
  },

  {
    path: '/campaign',
    name: 'Campaign',
    component: OldCampaignPage,
    meta: { requiresAuth: true }
  },

  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/self-value',
    name: 'SelfValue',
    component: SelfValueLanding,
  },
  {
    path: '/self-value/intro',
    name: 'SelfValueIntro',
    component: SelfValueIntro,
  },
  {
    path: '/self-value/questions',
    name: 'SelfValueQuestions',
    component: SelfValueQuestions,
  },
  {
    path: '/self-value/report',
    name: 'SelfValueReport',
    component: SelfValueReport,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const restoreAuthState = () => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('username') || '';

  if (token && !store.state.token) {
    store.commit('auth_success', { token, user });
  }
};

router.beforeEach((to, from, next) => {
  restoreAuthState();

  if (to.name === 'Login' && store.getters.isLoggedIn) {
    next('/dashboard');
    return;
  }

  if (to.matched.some(record => record.meta.requiresAuth) && !store.getters.isLoggedIn) {
    next({ name: 'Home', query: { loginRequired: '1' } });
    return;
  }

  next();
});


export default router;
