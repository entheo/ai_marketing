<template>
  <n-spin :show='waitRegister'>
    <template #description>
      <n-card :bordered='false'>稍等，正在完成注册...</n-card>
    </template>
    <n-form ref="formRef" :rules="rules"  :model="modelRef">
        <n-form-item-row path="userName" label="用户名">
            <n-input v-model:value="modelRef.userName" minlength="5" maxlength="10" placeholder="5~10位字符" />
        </n-form-item-row>
        
         
         <!--验证模块-->

        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="modelRef.password"
            type="password"
            @input="handlePasswordInput"
            @keydown.enter.prevent
            minlength="6"
            placeholder="至少6个字符"
            show-password-on="click"
            />
        </n-form-item>
    
        <n-form-item
          ref="rPasswordFormItemRef"
          first
          path="reenteredPassword"
          label="重复密码">

          <n-input
            v-model:value="modelRef.reenteredPassword"
            :disabled="!modelRef.password"
            type="password"
            @keydown.enter.prevent
            placeholder=""
            clearable/>
        </n-form-item>


        <n-form-item-row path="invitationCode" label="邀请码">
            <n-input v-model:value="modelRef.invitationCode" placeholder=""/>
        </n-form-item-row>
        
    </n-form>
    <n-button @click="register" 
      :disabled="modelRef.userName === null"
      type="primary" block secondary strong>
          注册
    </n-button>
  </n-spin>
</template>

<script setup>
import {NSpin,NCard,useNotification,NFormItem,NFormItemRow,NForm,NButton,NInput} from 'naive-ui';
import {ref,defineExpose} from 'vue';
import {useStore} from 'vuex';
import {useRouter} from 'vue-router';
import axios from 'axios';

//注册表单操作



const router=useRouter();

//注册方法
const notification =useNotification();
const waitRegister = ref(false);

//表单验证,通过后进行注册
const formValidated=ref(false);
const formValidateCheck = async(e)=>{
    return new Promise((resolve,reject)=>{
      e.preventDefault();
      formRef.value?.validate((errors)=>{
        if(!errors){
          console.log('验证成功')
          formValidated.value=true;
          resolve();
            }
        else{
          console.log('验证失败');
          reject('表单验证失败')}
          })
    })};

//注册
const toRegister=async()=>{
    console.log('开始注册');
    try{
      waitRegister.value=true;
      const response = await axios.post('/account/register/',
        {
          timeout:50000,
          username:modelRef.value.userName,
          password:modelRef.value.password,
          invitation_code:modelRef.value.invitationCode,
        },
        {
          headers:{
                //'X-CSRFToken': csrfToken.value,
                }
        });
      console.log(response);
<<<<<<< HEAD
      waitRegister.value=false;
      console.log(router);
<<<<<<< HEAD
      await router.push('/dashboard').then(()=>{
          console.log('跳转成功');  
      }).catch((err)=>{
          console.log('跳转失败',err);  
      });
=======
      await router.push(registeredNextPath.value);
>>>>>>> efbcd573d396de71828a5759dcdc00b1464cdbee
    }
    catch(err){
        console.log(err.response);
        if(err.response.status==400 && err.response.data.invitation_code){
=======
      console.log('注册成功');
      }catch(err){
         console.log(err) ;
         waitRegister.value=false;
         if(err.response.status==400 && err.response.data.invitation_code){
>>>>>>> dev
          notification.error({
              content:err.response.data.invitation_code[0],
              duration:2800,
              })}
         else if (err.response.status==400 && err.response.data.username[0]=='users with this username already exists.'){
             console.log('用户名重复');
             notification.error({
                 content:'用户名已存在，请重新注册',
                 duration:2800})
             }
     }}
    
const register=async(e)=>{
    waitRegister.value=true;
    try{
      await formValidateCheck(e);
      if(formValidated.value){
        await toRegister();
        loginUsername.value = modelRef.value.userName;
        loginPassword.value = modelRef.value.password;
        login();
        }
    }catch(err){
        console.log(err);
        waitRegister.value=false
           }    
   };

//密码验证

const formRef = ref(null);
const rPasswordFormItemRef = ref(null);

// 响应式表单数据
const modelRef = ref({
  userName:null,
  password: null,
  reenteredPassword: null,
  invitationCode:null,
});


//表单验证规则
const rules = {
  userName:[
    {
        required:true,
        validator(rule,value){
            if(!value){
                return new Error("请填写用户名");
                }else if (value.length<5 || value.length>10){
                    return new Error('字数须在5~10之间')}
                    return true;
            },
            triggr:["input","blur"]
        }
  ],
  password: [
    {
      required: true,
      validator(rule,value){
          if(value.length<6){
              return new Error("须至少6位")}
          },
      message: "请输入密码",
    },
  ],
  reenteredPassword: [
    {
      required: true,
      message: "请再次输入密码",
      trigger: ["password-input", "blur"]
    },
    
    {
      validator: validatePasswordSame,
      message: "两次密码输入不一致",
      trigger: ["blur", "password-input"]
    }
  ],
  invitationCode:[
    {
        required:true,
        message:"请输入邀请码",
        }
  ]
};


function validatePasswordSame(rule, value) {
  try{
  return value === modelRef.value.password;
  }catch(error){
      console.error(error)} 
  
  }

const handlePasswordInput=()=> {
  if(modelRef.value.reenteredPassword){
    console.log(modelRef.value.reenteredPassword);
    rPasswordFormItemRef.value?.validate({ trigger: "password-input" });
}}

//登录操作
const loginUsername=ref(null);
const loginPassword=ref(null);
const authStore = useStore();
const login = async () => {
    try{
        const response = await axios.post('/account/login/',
        {
          timeout:50000,
          username: loginUsername.value,
          password: loginPassword.value,
          keep_logged_in_for_days: '7',
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
        await router.push('/dashboard');

        }catch(err){
            console.log("登录失败：",err)
        }
    }
defineExpose({register});
</script>

<style>
.n-input{
    text-align:left}
</style>
