<template>
<div class="page-container" style="height: 100vh; overflow: hidden;text-align:left">
  <div class="flex-container" style="display: flex; justify-content: space-between;height:100%">
    
    <n-card>
      <n-form @submit.prevent="CampaignForm">
         
         <n-form-item label="title">
             <n-h5>本次活动名称</n-h5>
             <n-input v-model:value="campaignInfo.title" clearable size="large"></n-input>
         </n-form-item>
          
         <n-form-item label="start_time">
            <n-h5>开始与结束时间</n-h5>
            <n-date-picker v-model:value="dateRange" type="datetimerange" clearable />
         </n-form-item>

         <n-form-item>
             <n-h5>当前营销阶段</n-h5>
             <n-select v-model:value="campaignInfo.stage" size="large" :options="stageOptions" @update:value="handleUpdateValue" clearable />
         </n-form-item>
         <div class="tricks">
         <n-card title="📖 本阶段参考策略" embedded :bordered="false" >
           <div v-html="campaignStrategy"></div>
         </n-card> 
         </div>
         <n-form-item>
             <n-h5>关键目标</n-h5>
             <n-input v-model:value="campaignInfo.objectives" type="textarea" clearable size="large" default="fsdfsf"></n-input>
         </n-form-item>
         
         <n-form-item>
             <n-h5>目标客户画像</n-h5>
             <n-input v-model:value="campaignInfo.personaDesc" type="textarea" clearable size="large"></n-input>
         </n-form-item>

         <n-form-item>
             <n-h5>产品或服务名称</n-h5>
             <n-input v-model:value="campaignInfo.productName" clearable size="large"></n-input>
         </n-form-item>

         <n-form-item>
             <n-h5>独特卖点</n-h5>
             <n-input v-model:value="campaignInfo.productUsp" type="textarea" clearable size="large"></n-input>
         </n-form-item>

         <n-form-item>
             <n-h5>主要营销场景</n-h5>
             <n-input v-model:value="campaignInfo.scenarios" type="textarea" clearable size="large"></n-input>
         </n-form-item>
         
         <n-button @click="CampaignForm">提交</n-button>

      </n-form>
    </n-card>

    <n-card style="width: 45%;height:100%;overflow-y:auto">
      <n-card v-show="!has_brands" embedded>
      {{userName}}还未建立品牌档案？
      <n-button @click="activate('left')" secondary>添加</n-button>
      
      </n-card>

      <n-card v-show="!has_product" embedded>
      还未建立产品档案?
      <n-button secondary>添加</n-button>
      </n-card>
      
      <n-form @submit.prevent="submitForm"> 
        <n-card v-show="has_brands" title="当前品牌" embedded>
            <n-select v-model:value="selectValue" :options="options" />
         <n-button @click="activate('left')">
            详情
          </n-button>
        </n-card>

        <n-card v-show="has_product" title="当前产品" embedded>
          <n-select v-model:value="selectValue" :options="options" />
          <n-button @click="activate('left')">
            详情
          </n-button>
        </n-card>
        <n-card :bordered="false">
        <n-form-item label="上下文">
          <n-h5 prefix="bar">上下文</n-h5>
          <n-input v-model:value="formData.context" round clearable size="large" type="textarea" placeholder="上下文"></n-input>
        </n-form-item>
        </n-card>
         <n-card :bordered="false">
        <n-form-item label="写作目标">
          <n-h5 prefix="bar">写作目标</n-h5>
          <n-input v-model:value="formData.goal"  round clearable size="large" type="textarea" placeholder="写作目标"></n-input>
        </n-form-item>
        </n-card>
         <n-card :bordered="false">
        <n-form-item label="行文风格">
         <n-h5 prefix="bar">行文风格</n-h5>
         <n-input v-model:value="formData.style"  round clearable size="large" type="textarea" placeholder="行文风格"></n-input>
        </n-form-item>
        </n-card>
         <n-card :bordered="false">
        <n-form-item label="情绪语气">
          <n-h5 prefix="bar">情绪语气</n-h5>
          <n-input v-model:value="formData.tone"  round clearable size="large" type="textarea" placeholder="情绪语气"></n-input>
        </n-form-item>
        </n-card>
        <n-card :bordered="false">
        <n-form-item label="受众画像">
          <n-h5 prefix="bar">受众画像</n-h5>
          <n-input v-model:value="formData.audience"  round clearable size="large" type="textarea" placeholder="受众画像"></n-input>
        </n-form-item>
        </n-card>
        <n-card :bordered="false">
        <n-form-item label="输出要求">
          <n-h5 prefix="bar">输出要求</n-h5>
          <n-input v-model:value="formData.output"  round clearable size="large" type="textarea" placeholder="输出要求"></n-input>
        </n-form-item>
        </n-card>
        <n-button type="primary" @click="submitForm">提交</n-button>
      </n-form>
      
      <!--品牌信息-->
       <n-drawer v-model:show="active" :width="502" :placement="placement">
             <n-drawer-content title="brandInfo">
               <n-card>
               <n-form @submit.prevent="newBrandForm">
                 <n-form-item label="name">
                   <n-h5 prefix="bar">品牌名称</n-h5>
                   <n-input v-model:value="newBrandData.chinese_name" clearable size="large" type="text" placeholder="中文名称"></n-input>
                   <n-input v-model:value="newBrandData.english_name" clearable size="large" type="text" placeholder="英文名称"></n-input>

                </n-form-item>
                 <n-form-item label='values'>
                   <n-h5 prefix="bar">价值观理念</n-h5>
                   <n-input v-model:value="newBrandData.values" round clearable size="large" type="textarea"></n-input>
                 </n-form-item> 
              <n-button type="primary" @click="newBrandForm">提交</n-button> 
               </n-form>
             </n-card>  
             </n-drawer-content>
         </n-drawer>
    
    </n-card>
    <n-card style="width: 55%;height:100%;overflow-y:auto">
      {{message}}
    </n-card> 


  </div>
</div>
</template>
<script setup>
  import { NDatePicker, NButton, NForm, NCard, NInput, NH5, NSelect, NDrawer} from 'naive-ui';
  import {onBeforeMount} from 'vue'; 
  import axios from 'axios';
  import { ref } from 'vue';   
  
  const dateRange = ref([118313526e4, Date.now()]);
  const userName = ref('');
  const has_brands = ref(false);
  console.log(has_brands);
  //const has_product = ref(localStorage.created_product.length!0);
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
  const message = ref('');
  const active = ref(false);
  const placement = ref("right");
  const activate = (place) => {
      active.value = true
      placement.value = place
          };
  const selectValue = ref(null);
  const stageOptions = [
      {
          label:"意识阶段：客户初识，需要建立初步印象",
          value:"stage0",
          },
      {
          label:"兴趣阶段：激发客户兴趣，增强了解意愿",
          value:"stage1",
          },
      {
          label:"考虑阶段：提供决策思路，提升客户购买或相关行动可能性",
          value:"stage2",
          },
      {
          label:"意向阶段：帮助客户下决心，强化购买或相关行动意向",
          value:"stage3",
          },
      {
          label:"行动阶段：提出明确行动方式并号召，促使行动落地",
          value:"stage4",
          },
      {
          label:"忠诚度建立阶段：提供优质差异化服务价值，建立客户忠诚度",
          value:"stage5",
          },
      {
          label:"推荐阶段：借助满意度较高的客户实现口碑推荐",
          value:"stage6",
          },
      ];


  const options = [
      {
             label: "Everybody's Got Something to Hide Except Me and My Monkey",
             value: "song0",
             disabled: true
           },
           {
             label: "Drive My Car",
             value: "song1"
           },
           {
             label: "Norwegian Wood",
             value: "song2"
           },
           {
             label: "You Won't See",
             value: "song3",
             disabled: true
           }];

  
  const campaignStrategy = ref('');
  const campaignInfo = ref({
      personaDesc:'',
      title:'',
      objectives:'',
      senarios:'',
      productName:'',
      productUsp:'',
      stage:''
      });

  const handleUpdateValue = (value, option) => {
      switch(value){
          case 'stage0':
              campaignInfo.value.objectives= ref(
                "参考建议：品牌提及次数、相关内容分享次数");
              campaignStrategy.value = 
               "本阶段参考策略：<br>"+
               "1.利用社群成员分享品牌故事<br>"+
               "2.强调品牌价值观和创始人IP<br>3.提供有价值的内容";
          break;
          case 'stage1':
              campaignInfo.value.objectives= ref(
              "参考建议：用户问询次数、用户间互动次数、内容关注度(浏览量)");
              campaignStrategy.value = 
              "本阶段参考策略：<br>1.提供深度内容，如使用教程、效果前后对比;<br>2.社群互动，如问答、讨论;<br>3.创始人参与讨论"
          break;
          case 'stage2':
              campaignInfo.value.objectives=ref(
              "参考建议：用户试用率、用户反馈、产品比较次数");
              campaignStrategy.value = 
              "本阶段参考策略：<br>1.分享用户评价和案例研究;<br>2.提供产品试用或样品;<br>3.强调产品的独特卖点（USP）";
          break;
          case 'stage3':
              campaignInfo.value.objectives=ref(
              "参考建议：意向用户数量、优惠使用率、用户咨询次数");
              campaignStrategy.value = 
              "本阶段参考策略：<br>1.根据用户反馈设计个性化服务;<br>2.提供社群专属优惠;<br>3.强调稀缺性，如限量、限时";
          break;
          case 'stage4':
              campaignInfo.value.objectives=ref(
              "参考建议：转化率、购买数量、平均订单价值");
              campaignStrategy.value = 
              "本阶段参考策略：<br> 1.设置类似一键购买或快速购买流程;<br>2.提供清晰的CTA<br>;3.社群内快速响应";
          break;
          case 'stage5':
              campaignInfo.value.objectives=ref(
              "参考建议：重复购买率、会员活跃度、用户推荐率");
              campaignStrategy.value = 
              "本阶段参考策略：<br>1.设立会员分层机制;<br>2.提供定期的用户关怀;<br>3.收集用户反馈进行产品迭代";
          break;
          case 'stage6':
              campaignInfo.value.objectives=ref(
              "参考建议：-新用户增长率、相关推荐数量、社群扩张速度");
              campaignStrategy.value =
              "本阶段参考策略：<br>1.设计推荐计划和奖励机制;<br>2.鼓励用户分享使用体验;<br>3.利用用户生成内容";
          break;
          default:
              campaignInfo.value.objectives=ref('');
          }
      console.log("value: " + JSON.stringify(value));
      console.log("option: " + JSON.stringify(option));
      };

  const CampaignForm = () =>{
      try{
          /*
          const resp =  await axios.get('http://localhost:8005/account/auth/',{
            headers: {
                'Authorization': `Bearer ${token}` // 设置请求头
                }});
         */ }catch (error) {
        console.error('Failed to fetch user info:', error);
      }

      }
  const formData = ref({
      context:'',
      goal:'',
      style:'',
      tone:'',
      audience:'',
      output:''}
      );
  const submitForm = () => {
               axios.post('http://localhost:8005/api/response/', formData)
                 .then(resp => {
                   // 处理你后端返回的response
                   console.log(resp);
                   message.value = resp.data.message;
                 })
                 .catch(err => {
                   console.log(err);
                 });
                 
           };
  const newBrandData = ref({
          chinese_name:'',
          english_name:'',
          values:'',
          audience:'',
          });

  const newBrandForm = () => {
      console.log(newBrandData.value);
      const token = localStorage.getItem('token');    
      axios.post('http://localhost:8005/marketing/brands/', newBrandData.value,
          {   
            withCredentials: true,  
            headers: {
              'X-CSRFToken': csrfToken.value,  // 使用组件状态中的CSRF token
              'Authorization': `Bearer ${token}` // 设置请求头
              },
           }   
          )   
            .then(response => {
              // 处理你后端返回的response
              console.log(response);
            })  
            .catch(err => {
              console.log(err);
          }); 
        };

const fetchUserInfo = async() => {
      const token = localStorage.getItem('token');
      console.log(token);
      try {
        const resp =  await axios.get('http://localhost:8005/account/auth/',{
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
    

onBeforeMount(async()=>{
    fetchUserInfo();
    })
</script>

<style>
.tricks {
    font-size:0.8em;
}
</style>
