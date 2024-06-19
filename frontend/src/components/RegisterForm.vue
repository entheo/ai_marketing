<template>
    <n-form ref="formRef" :rules="rules"  :model="modelRef">
        <n-form-item-row path="userName" label="用户名">
            <n-input v-model:value="modelRef.userName" minlength="5" maxlength="10" placeholder="5~10位字符" />
        </n-form-item-row>
        
        <!--
        <n-form-item-row label="密码" :feedback="validateInfos.password>
            <n-input v-model:value="registerPassword" maxlength="15" placeholder="最多15位字符"/>
        </n-form-item-row>
          
        <n-form-item-row label="重复密码">
            //<n-input passively-activated @input="checkRePassword" v-model:value="rePassword" placeholder=""/>
            <n-input
                v-model:value="rePassword"
                :disabled="!model.password"
                type="password"
                @keydown.enter.prevent
                placeholder=""/>
        </n-form-item-row>
         -->
         
         
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
    <n-button @click="formValidateCheck" 
      :disabled="modelRef.userName === null"
      type="primary" block secondary strong>
          注册
    </n-button>

</template>
<script setup>
import {useNotification,NFormItem,NFormItemRow,NForm,NButton,NInput} from 'naive-ui';
import {ref,defineExpose} from 'vue';
import {useRouter} from 'vue-router';
import axios from 'axios';

//注册表单操作



const router=useRouter();
const registeredNextPath = ref('/dashboard');

//注册方法
const notification =useNotification()
const register=async()=>{
    if(formValidated.value===true){
    try{
      const response = await axios.post('/account/register/',
      {
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
      await router.push(registeredNextPath.value);
    }
    catch(err){
        console.log(err.response);
        if(err.response.status==400 && err.response.data.invitation_code){
          notification.error({
              content:err.response.data.invitation_code[0],
              duration:2800,
              })}

        console.log('注册失败:',err)}
    
 }}

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

//表单验证,通过后进行注册
const formValidated=ref(false);
const formValidateCheck = async(e)=>{
    e.preventDefault();
    formRef.value?.validate((errors)=>{
        if(!errors){
            console.log('验证成功');
            formValidated.value=true;
            register();
            }else{
                console.log('验证失败');
                }
            });
    };

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


defineExpose({register});
</script>

<style>
.n-input{
    text-align:left}
</style>
