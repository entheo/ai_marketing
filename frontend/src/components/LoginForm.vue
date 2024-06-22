<template>
<n-spin :show='waitLogin'>
  <template #description>
    <n-card :bordered='false'>稍等,正在完成登录...</n-card>
  </template>
<n-form>
    <n-form-item-row label="用户名">
        <n-input v-model:value="loginUsername" placeholder=""/>
          </n-form-item-row>
          <n-form-item-row label="密码">
            <n-input v-model:value="loginPassword" placeholder="" type="password" show-password-on="click" :maxlength="15"/>
          </n-form-item-row>
        </n-form>
        <n-button @click="login" type="primary" block secondary strong>
          登录
    </n-button>
 </n-spin>
</template>

<script setup>
import {NSpin,NCard,useNotification,NButton,NInput,NForm,NFormItemRow} from 'naive-ui';
import {ref,defineExpose} from 'vue';
import {useStore} from 'vuex';
import {useRouter} from 'vue-router';
import axios from 'axios';


//通用变量
const authStore = useStore();
const router = useRouter();

//登录表单操作
const loginUsername = ref('');
const loginPassword = ref('');
const keepLoggedInForDays = ref('7'); // 默认设置为7天，通过select控件让用户可选择
const notification=useNotification();
const waitLogin=ref(false);
const login = async () => {
    try{
        waitLogin.value=true;
        const response = await axios.post('/account/login/', 
        {   
          timeout:50000,
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
        //const csrf_token = response.data.csrf_token;
        //console.log('csrf_token:',csrf_token);
        localStorage.setItem('token', token);
        await authStore.commit('auth_success', { token, user });
        console.log("登录成功：",loginUsername.value); 
        waitLogin.value=false;
        await router.push('/dashboard');
        
        }catch(err){
            if(err.response.status==400){
                notification.error({
                    content:err.response.data.message,
                    duration:2500
                    })
            }
            console.log("登录失败：",err)
            waitLogin.value=false;
        }
    }



//暴露方法
defineExpose({login});
</script>

<style>
.n-input{
    text-align:left}
</style>

