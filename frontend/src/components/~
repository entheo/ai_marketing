<!--./CreateForm.vue-->
<template>
<n-form>
<n-form-item label="title">
             <n-h5>本次活动名称</n-h5>
             <n-input v-model:value="campaignInfo.title" clearable size="large"></n-input>
         </n-form-item>

         <n-form-item label="start_time">
            <n-h5>开始与结束时间</n-h5>
            <n-date-picker v-model:value="campaignInfo.dateRange" type="datetimerange" clearable />
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

         <n-button @click="createCampaign">确认</n-button>
</n-form>
</template>
<script setup>
import {ref} from 'vue';
import { NDatePicker, NButton, NForm,NFormItem, NCard, NInput, NH5, NSelect} from 'naive-ui';
const campaignInfo = ref({
      title:'',
      objectives:'',
      dateRange:'',
      stage:''
      });
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

const createCampaign = () =>{
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

</script>
<script>
  export default{
      name:'CreateForm'
      };
</script>
