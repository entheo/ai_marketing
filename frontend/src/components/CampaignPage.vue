<template>
<div class="page-container" style="height: 100vh; overflow: hidden;text-align:left">
    
    <n-card>
     <create-campaign-form @createCampaignInfo="handleCampaignInfo" ref="campaignForm"/> 
     <n-button @click="submitCampaignForm" type="info">提交</n-button>
     </n-card>
</div>



</template>
<script setup>
  //import { NDatePicker, NButton, NForm, NCard, NInput, NH5, NSelect, NDrawer} from 'naive-ui';
  import {NCard,NButton} from 'naive-ui';
  import {onBeforeMount} from 'vue'; 
  //import axios from 'axios';
  import { ref } from 'vue';   
  import CreateCampaignForm from './CreateCampaignForm.vue';
  import {useStore} from 'vuex';
  /*
  const getCsrfToken = () => {
    let csrfToken = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            csrfToken = decodeURIComponent(cookie.substring('csrftoken='.length));
            break;
        }   
      }   
    }   
    return csrfToken;
  };
  const csrfToken = ref(getCsrfToken());
  */

  const campaignForm = ref(null);
  const submitCampaignForm = () => {
      campaignForm.value.createCampaign();
      }

  const handleCampaignInfo = (message) => {
      console.log(message);
      /*
               axios.post('http://localhost:8005/api/response/', formData)
                 .then(resp => {
                   // 处理你后端返回的response
                   console.log(resp);
                   message.value = resp.data.message;
                 })
                 .catch(err => {
                   console.log(err);
                 });
                 
          */ };

/*
  const userName = ref('');
  const fetchUserInfo = async() => {
      const token = localStorage.getItem('token');
      console.log(token);
      try {
        const resp =  await axios.get('/account/auth/',{
            headers: {
                'Authorization': `Bearer ${token}` // 设置请求头
                }});
        console.log('验证结果:')
        console.log(resp.data);
        userName.value = resp.data.username;
        has_brands.value = resp.data.created_brands.length;
        //localStorage.setItem('username',resp.data.username);
          } catch (error) {
        console.error('Failed to fetch user info:', error);
      }
    };
  */

//定义之前已获得的相关建议

onBeforeMount(async()=>{
    const store = useStore();
    const preData = ref(null);
    preData.value = store.getters.temp_campaign_data;
    console.log(preData.value)
   // fetchUserInfo();
    })
</script>

<style>
.tricks {
    font-size:0.8em;
}
</style>
