<template>
  <n-form label-placement="left" require-mark-placement="right-hanging" label-width="auto" size="large">
    
    <n-form-item label="为本次营销活动起一个名字吧？">
      <n-input v-model:value="campaignInfo.title" clearable size="large" placeholder=""/>
    </n-form-item>

    <n-form-item label="活动开始与结束时间是？">
            <n-date-picker v-model:value="campaignInfo.dateRange" type="datetimerange" clearable placeholder=""/>
         </n-form-item>
      
         <n-form-item label="当前位于哪个营销阶段？">
             <n-select v-model:value="campaignInfo.stage" size="large" :options="stageOptions" @update:value="handleUpdateValue" clearable />
         </n-form-item>
        
        <div class="tricks" v-show="has_strategy">
          <n-card  embedded :bordered="false" >
            <div v-html="campaignStrategy"></div>
         </n-card>
       </div>

         <n-form-item label="期待达到的效果与关键目标是什么？:">
             <n-input v-model:value="campaignInfo.objectives" type="textarea" clearable size="large" placeholder=""/>
         </n-form-item>

         <n-button v-show="false" @click="createCampaign">确认</n-button>
</n-form>
</template>
<script setup>
import {onBeforeMount,ref,defineEmits,defineExpose} from 'vue';
import { NDatePicker, NButton, NForm,NFormItem, NCard, NInput, NSelect} from 'naive-ui';
import {useStore} from 'vuex';

//组件挂载前加载数据
onBeforeMount(()=>{
    const store = useStore();
    preData.value = store.getters.temp_campaign_data;
    handleCampaignInfo();
    });
const preData = ref(null);
const campaignInfo = ref({});
const handleCampaignInfo=()=>{
    console.log(typeof(preData.value));
    if(preData.value && JSON.stringify(preData.value)!=='{}' ){
       campaignInfo.value.stage = preData.value.campaign_background.stage;
       campaignInfo.value.objectives = preData.value.campaign_background.objectives;
       }   
    }
/*
const campaignInfo = ref({
      title:'',
      objectives:'',
      dateRange:ref(null),
      stage:''
      });*/

const stageOptions = [
      {
          label:"1.意识阶段：客户初识，需要建立初步印象",
          value:"意识阶段：客户初识，需要建立初步印象",
          //value:"stage0",
          },
      {
          label:"2.兴趣阶段：激发客户兴趣，增强了解意愿",
          value:"兴趣阶段：激发客户兴趣，增强了解意愿",
          //value:"stage1",
          },
      {
          label:"3.考虑阶段：提供决策思路，提升客户购买或相关行动可能性",
          value:"考虑阶段：提供决策思路，提升客户购买或相关行动可能性",
          //value:"stage2",
          },
      {
          label:"4.意向阶段：帮助客户下决心，强化购买或相关行动意向",
          value:"意向阶段：帮助客户下决心，强化购买或相关行动意向",
          //value:"stage3",
          },
      {
          label:"5.行动阶段：提出明确行动方式并号召，促使行动落地",
          value:"行动阶段：提出明确行动方式并号召，促使行动落",
          //value:"stage4",
      },
      {
          label:"6.忠诚度建立阶段：提供优质差异化服务价值，建立客户忠诚度",
          value:"忠诚度建立阶段：提供优质差异化服务价值，建立客户忠诚度",
          //value:"stage5",
          },
      {
          label:"7.推荐阶段：借助满意度较高的客户实现口碑推荐",
          value:"推荐阶段：借助满意度较高的客户实现口碑推荐",
          //value:"stage6",
          },
      ];
const has_strategy = ref(false);
const campaignStrategy = ref('');
const handleUpdateValue = (value, option) => {
      has_strategy.value = true;
      switch(value){
          case '意识阶段：客户初识，需要建立初步印象':
              campaignInfo.value.objectives= ref(
                "参考建议：品牌提及次数、相关内容分享次数");
              campaignStrategy.value =
               "📖<b>本阶段参考策略</b>：<br>"+
               "1.利用社群成员分享品牌故事<br>"+
               "2.强调品牌价值观和创始人IP<br>3.提供有价值的内容";
          break;
          case '兴趣阶段：激发客户兴趣，增强了解意愿':
              campaignInfo.value.objectives= ref(
              "建议考虑关键目标：客户主动问询次数、客户间交流次数、内容关注度(浏览量)");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br>1.提供深度内容，如使用教程、效果前后对比;<br>2.社群互动，如问答、讨论;<br>3.创始人参与讨论"
          break;
          case '考虑阶段：提供决策思路，提升客户购买或相关行动可能性':
              campaignInfo.value.objectives=ref(
              "参考建议：用户试用率、用户反馈、产品比较次数");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br>1.分享用户评价和案例研究;<br>2.提供产品试用或样品;<br>3.强调产品的独特卖点（USP）";
          break;
          case '意向阶段：帮助客户下决心，强化购买或相关行动意向':
              campaignInfo.value.objectives=ref(
              "参考建议：意向用户数量、优惠使用率、用户咨询次数");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br>1.根据用户反馈设计个性化服务;<br>2.提供社群专属优惠;<br>3.强调稀缺性，如限量、限时";
          break;
          case '行动阶段：提出明确行动方式并号召，促使行动落':
              campaignInfo.value.objectives=ref(
              "参考建议：转化率、购买数量、平均订单价值");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br> 1.设置类似一键购买或快速购买流程;<br>2.提供清晰的CTA<br>;3.社群内快速响应";
          break;
          case '忠诚度建立阶段：提供优质差异化服务价值，建立客户忠诚度':
              campaignInfo.value.objectives=ref(
              "参考建议：重复购买率、会员活跃度、用户推荐率");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br>1.设立会员分层机制;<br>2.提供定期的用户关怀;<br>3.收集用户反馈进行产品迭代";
          break;
          case '推荐阶段：借助满意度较高的客户实现口碑推荐':
              campaignInfo.value.objectives=ref(
              "参考建议：-新用户增长率、相关推荐数量、社群扩张速度");
              campaignStrategy.value =
              "📖<b>本阶段参考策略</b>：<br>1.设计推荐计划和奖励机制;<br>2.鼓励用户分享使用体验;<br>3.利用用户生成内容";
          break;
          default:
              campaignInfo.value.objectives=ref('');
          }
      console.log("value: " + JSON.stringify(value));
      console.log("option: " + JSON.stringify(option));
      };
const emit = defineEmits(['createdCampaignInfo']);
const createCampaign = () =>{
      emit('createdCampaignInfo',campaignInfo.value);
      console.log('createCampaign');
      console.log(campaignInfo.value);
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
defineExpose({createCampaign});
</script>
<script>
  export default{
      name:'CreateCampaignForm'
      };
</script>
<style>
.tricks{
    margin-bottom:20em;
    width:100%}
</style>
