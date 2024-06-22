<!-- src/components/HomePage.vue -->
<template>
  <n-layout position="absolute">
  <n-layout-header></n-layout-header>
  <n-layout-content> 
  <n-grid  class="login" cols="2 s:2 m:2 l:7 xl:7 2xl:7" responsive="screen">
     
     <!--品牌信息-->
     <n-grid-item span=4>
        <div class='brand'>
          <h1>步步为营</h1>
        </div>
        
        <div class='slogan'>
          <p>一个帮你追求更高营销效果的AI脚手架</p>
          <a href="https://docs.qq.com/form/page/DZnZ4dWpyck56Y3VT“" target="_blank">
          申请邀请码
          </a>
        </div>
      </n-grid-item>
    
     <!--登录&注册组件-->
     <n-grid-item :offset="0" span=2>
       <n-spin :show='wait'>
        <n-card>
         <login-register/>
        </n-card>
       </n-spin>
      </n-grid-item>
  </n-grid>    
  </n-layout-content>
  <!--n-layout-footer position="absolute">
   footer
  </n-layout-footer-->
  </n-layout>
</template>

<script setup>
//import axios from 'axios';
import { onMounted } from 'vue';
import { useStore } from 'vuex';
//import { useRouter } from 'vue-router';
import LoginRegister from './LoginRegister.vue';
import {NLayout,NLayoutHeader,NGrid,NGridItem,NCard} from 'naive-ui';


onMounted(()=>{
    document.title="步步为营"
    })
// 用于获取csrftoken的函数
/*
function getCsrfToken() {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken'))
    ?.split('=')[1];
}*/

const authStore = useStore();
console.log(authStore.getters.isLoggedIn); // 使用getters来访问状态
// 在组件加载时获取CSRF token
//const csrfToken = ref(getCsrfToken());
/*
const registerUsername = ref('');
const registerPassword = ref('');
const invitation = ref('');
const router = useRouter();
const handleRegisterSubmit = async () => {
      try{
          const response = await axios.post('/account/register/', {
            username: registerUsername.value,
            password: registerPassword.value,
            invitation_code: invitation.value
          },
          {
          headers: {
            'X-CSRFToken': csrfToken.value,
            }
          });
          console.log(response);
          console.log("注册成功，用户名: ", registerUsername.value);
          await router.push('/login');
          }
     catch (err) {
            console.log(err);
           }
       };
*/
/*
export default {
  name: 'HomePage',
  setup() {
    const authStore = useStore();
    console.log(authStore.getters.isLoggedIn); // 使用getters来访问状态
    // 在组件加载时获取CSRF token
    const csrfToken = ref(getCsrfToken());
    const loginUsername = ref('');
    const loginPassword = ref('');
    const keepLoggedInForDays = ref('7'); // 默认设置为7天，通过select控件让用户可选择

    const registerUsername = ref('');
    const registerPassword = ref('');
    const invitation = ref('');

    const router = useRouter();

    const handleLoginSubmit = async () => {
      try{
          console.log(loginUsername.value);
          console.log(loginPassword.value);
          const response = await axios.post('/account/login/', {
            username: loginUsername.value,
            password: loginPassword.value,
            keep_logged_in_for_days: keepLoggedInForDays.value
          },
         {
            withCredentials: true,
            headers: {
            'X-CSRFToken': csrfToken.value,
          }
        });

         console.log("登录成功，用户名: ", loginUsername.value);
         const token = response.data.token.access;
         const user = response.data.username;
         const csrf_token = response.data.csrf_token;
         console.log('csrf_token:');
         console.log(csrf_token);
         localStorage.setItem('token', token);
         await authStore.commit('auth_success', { token, user });
         await router.push('/dashboard');
          }
      catch (err) {
          console.log(err);
          }
        };
       

    const handleRegisterSubmit = async () => {
      try{
          const response = await axios.post('/account/register/', {
            username: registerUsername.value,
            password: registerPassword.value,
            invitation_code: invitation.value
          },
          {
          headers: {
            'X-CSRFToken': csrfToken.value,
            }
          });
          console.log(response);
          console.log("注册成功，用户名: ", registerUsername.value);
          await router.push('/login');
          }
     catch (err) {
            console.log(err);
           }
       };

    return {
      loginUsername,
      loginPassword,
      keepLoggedInForDays,
      registerUsername,
      registerPassword,
      invitation,
      handleLoginSubmit,
      handleRegisterSubmit,
      csrfToken, // 添加csrfToken到返回值中
      LoginForm,
    };
  },
};
*/
</script>

<style>
.n-grid{
    height:100%;
    align-items:center;
    }
.brand{
    font-size:3em;
    }
.slogan{
    margin-top:-2em;
    font-size:1.2em}
.card-tabs .n-tabs-nav--bar-type {
  padding-left: 4px;
}
</style>
