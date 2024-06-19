<template>

<n-layout position="absolute">
  
  <n-layout-header style="height: 64px; padding: 24px" bordered>
   步步为营
  </n-layout-header>
  
  <n-layout-content>
    <n-grid  cols="2 s:1 m:1 l:12 xl:12 2xl:12" responsive="screen">
      <n-grid-item span="4">
       
        <!--抽屉
        <n-button @click="doShowOuter">
        来一个！
        </n-button>
  
        <n-drawer v-model:show="showOuter" :width="502">
          <n-drawer-content title="斯通纳">
          《斯通纳》是美国作家约翰·威廉姆斯在 1965 年出版的小说。
            <n-button @click="doShowInner">再来一个!</n-button>
           </n-drawer-content>
           <n-drawer v-model:show="showInner" :width="251">
             <n-drawer-content title="斯通纳">
             《斯通纳》是美国作家约翰·威廉姆斯在 1965 年出版的小说。
             </n-drawer-content>
           </n-drawer>
        </n-drawer>
        -->
        
        
        <n-form >
          
          <!--营销目标-->
          <n-card>
            <n-form-item>
              <n-h5>营销阶段</n-h5>
              <n-select v-model:value="campaignInfo.stage" size="large" :options="stageOptions" @update:value="handleUpdateValue" clearable />
            </n-form-item>
         
            <div class="tricks">
              <n-card title="📖 本阶段参考策略" embedded :bordered="false" >
                <div v-html="campaignStrategy"></div>
              </n-card> 
            </div>

            <n-form-item>
             <n-h5>关键目标</n-h5>
             <n-input v-model:value="campaignInfo.objectives" type="textarea" clearable size="large"/>
            </n-form-item>
          </n-card>
          
          <!--目标受众画像-->
          <n-card>
            <n-form-item>
              <n-h5>目标客户画像</n-h5>
              <n-input v-model:value="campaignInfo.personaDesc" type="textarea" clearable size="large"/>
            </n-form-item>
            <n-form-item>
              <n-h5>相关心理动机</n-h5>
              <n-input v-model:value="campaignInfo.personaMotive" type="textarea" clearable size="large"/>
            </n-form-item>
          </n-card>
          
          <!--产品与服务-->
          <n-card>
            <n-form-item>
              <n-h5>产品或服务名称</n-h5>
              <n-input v-model:value="campaignInfo.productName" clearable size="large"/>
            </n-form-item>
            <n-form-item>
              <n-h5>独特卖点</n-h5>
              <n-input v-model:value="campaignInfo.productUsp" type="textarea" clearable size="large"/>
            </n-form-item>
            <n-form-item>
              <n-h5>品牌理念</n-h5>
              <n-input v-model:value="campaignInfo.brandValues" type="textarea" clearable size="large"/>
            </n-form-item>
          </n-card>
        
          <!--场景&情绪&文案要求-->
          <n-card>
            <n-form-item>
              <n-h5>主要营销场景</n-h5>
              <n-input v-model:value="campaignInfo.senarios" type="textarea" clearable size="large"/>
            </n-form-item>
            <n-form-item>
              <n-h5>期待传递情绪</n-h5>
              <n-input v-model:value="campaignInfo.emotions" type="textarea" clearable size="large"/>
            </n-form-item>
            <n-form-item>
              <n-h5>输出要求</n-h5>
              <n-input v-model:value="campaignInfo.output" type="textarea" clearable size="large"/>
            </n-form-item>
          </n-card>
          
          <n-button @click="submitForm">提交</n-button>
         

       </n-form>
    </n-grid-item>

    <!--展示结果-->
    <n-grid-item span="8">
     <n-card :show='gotResponse' :bordered='false'>{{preData.original}}</n-card>
     {{responseMessage}}
    </n-grid-item>
      
    </n-grid>
  </n-layout-content>
  
  <n-layout-footer>
  footer
  </n-layout-footer>

</n-layout>

</template>
<script setup>
  import { NInput,NLayout,NButton, NForm, NFormItem,NCard, NH5, NSelect,NLayoutContent,NLayoutHeader,NLayoutFooter,NGrid,NGridItem} from 'naive-ui';
  import {onBeforeMount} from 'vue'; 
  import axios from 'axios';
  import { ref } from 'vue';   
  import {useStore} from 'vuex';

  const userName = ref('');
  
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



  
  const campaignStrategy = ref('');

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
  const responseMessage = ref('');
  const campaignInfo = ref({});
  const gotResponse = ref(false);
  const submitForm = () => {
      console.log(csrfToken);
      const token = localStorage.getItem('token'); 
      const promptData = campaignInfo.value;
      promptData.type='new_copy';
      axios.post('/api/response/', promptData,{
                   withCredentials: true,
                   headers:{
                       'Authorization':`Bear ${token}`
                       }})
                 .then(resp => {
                   // 处理你后端返回的response
                   console.log(resp);
                   gotResponse.value=true;
                   responseMessage.value = resp.data.message;
                   
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
        //localStorage.setItem('username',resp.data.username);
          } catch (error) {
        console.error('Failed to fetch user info:', error);
      }
    };
    

const preData = ref({
    original:''});
onBeforeMount(async()=>{
    const store = useStore();
    preData.value = store.getters.temp_campaign_data;
    console.log(preData.value)
    updatePreData();
    fetchUserInfo();
    });

const updatePreData=()=>{
    if (preData.value && JSON.stringify(preData.value)!=="{}"){
        campaignInfo.value.stage =preData.value.campaign_background.stage;
        campaignInfo.value.objectives = preData.value.campaign_background.objectives;
        campaignInfo.value.personaDesc = preData.value.persona.desc;
        campaignInfo.value.personaMotive = preData.value.persona.motive;
        campaignInfo.value.productName = preData.value.product.name;
        campaignInfo.value.productUsp = preData.value.product.usp;
        campaignInfo.value.brandValues = preData.value.product.values;
        campaignInfo.value.senarios = preData.value.senario.place;
        campaignInfo.value.emotions = preData.value.senario.emotions;
        campaignInfo.value.original = preData.value.original;
        }
     submitForm();   

    }

</script>

<style>
.tricks {
    font-size:0.8em;
}
</style>
