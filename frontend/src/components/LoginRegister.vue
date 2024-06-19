<template>

    <n-tabs
      class="card-tabs"
      default-value="login"
      size="large"
      animated
      pane-wrapper-style="margin: 0 -4px"
      pane-style="padding-left: 4px; padding-right: 4px; box-sizing: border-box;"
    >

      <n-tab-pane name="login" tab="登录">
            <login-form/>
       <!--
        <n-form>
          <n-form-item-row label="用户名">
            <n-input v-model:value="loginUsername" placeholder=""/>
          </n-form-item-row>
          <n-form-item-row label="密码">
            <n-input v-model:value="loginPassword" placeholder="最长15位字符" type="password" show-password-on="click" :maxlength="15"/>
          </n-form-item-row>
        </n-form>
        <n-button @click="login" type="primary" block secondary strong>
          登录
        </n-button>
        -->
      </n-tab-pane>

      <n-tab-pane name="register" tab="注册">
        <register-form/>
        

        <!--
        <n-form>
          <n-form-item-row label="用户名">
            <n-input v-model:value="registerUsername" placeholder="" />
          </n-form-item-row>
          <n-form-item-row label="密码">
            <n-input v-model:value="registerPassword" :maxlength="15" placeholder="最长15位字符"/>
          </n-form-item-row>
          <n-form-item-row label="重复密码">
            <n-input v-model:value="registerRePassword" placeholder=""/>
          </n-form-item-row>
          <n-form-item-row label="邀请码">
            <n-input v-model:value="invitation_code" placeholder=""/>
          </n-form-item-row>
        </n-form>
        <n-button @click="register" type="primary" block secondary strong>
          注册
        </n-button>
        -->
      </n-tab-pane>
    </n-tabs>
 
</template>

<script setup>
import {NTabs,NTabPane} from 'naive-ui'
import {ref,defineExpose} from 'vue';
import {useStore} from 'vuex';
import {useRouter} from 'vue-router';
import axios from 'axios';
import RegisterForm from './RegisterForm.vue';
import LoginForm from './LoginForm.vue';


//通用变量
const authStore = useStore();
const router = useRouter();

//登录表单操作
const loginUsername = ref('');
const loginPassword = ref('');
const keepLoggedInForDays = ref('7'); // 默认设置为7天，通过select控件让用户可选择

const login = async () => {
    try{
        const response = await axios.post('/account/login/', 
        {   
          username: loginUsername.value,
          password: loginPassword.value,
          keep_logged_in_for_days: keepLoggedInForDays.value
        },  
        {   
          withCredentials: true,
          headers: {
            //先注销'X-CSRFToken': csrfToken.value,
          }   
        });
        const token = response.data.token.access;
        const user = response.data.username;
        const csrf_token = response.data.csrf_token;
        console.log('csrf_token:',csrf_token);
        localStorage.setItem('token', token);
        await authStore.commit('auth_success', { token, user });
        console.log("登录成功：",loginUsername.value); 
        await router.push('/dashboard');
        
        }catch(err){
            console.log("登录失败：",err)
        }
    }



//暴露方法
defineExpose({login});
</script>

<style>
.n-input{
    text-align:left}
</style>

