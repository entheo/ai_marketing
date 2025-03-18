import { createApp } from 'vue';
import App from './App.vue';
import {create} from 'naive-ui';
import router from './router'; 
import store from './store';
import axios from 'axios';

const naive = create();
const app = createApp(App);
//axios.defaults.baseURL = 'http://stepstowin.wetouch.cn'
axios.defaults.baseURL = 'http://localhost:8001'

app.use(naive);
app.use(router);
app.use(store);
app.mount('#app');


//createApp(App).mount('#app')
