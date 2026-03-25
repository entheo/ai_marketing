import { createApp } from 'vue';
import App from './App.vue';
import { create } from 'naive-ui';
import router from './router';
import store from './store';

import './styles/tokens.css';
import './styles/base.css';
import './styles/ui.css';

const naive = create();

async function bootstrap() {
  const app = createApp(App);

  app.use(naive);
  app.use(router);
  app.use(store);

  if (localStorage.getItem('token')) {
    try {
      await store.dispatch('checkAuth')
    } catch (error) {
      console.error('登录态校验失败：', error)
    }
  }

  app.mount('#app');
}

bootstrap();
