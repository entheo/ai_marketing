<!--SimpleCampaignForm-->
<template>
    <n-form label-placement="left" require-mark-placement="right-hanging" :label-width="labelWidth" size="large">
     
        <n-form-item label="当前位于哪个营销阶段？">
             <n-select v-model:value="campaignInfo.stage" size="large" :options="stageOptions" @update:value="handleUpdateValue" clearable placeholder="点击选择↓ （参考营销漏斗的不同阶段）"/>
         </n-form-item>
        
        <div class="trick" v-show="has_strategy">
          <n-card  embedded :bordered="false" >
            <n-icon><bulb-outline/></n-icon>阶段特点提示：
            <div v-html="markdownStrategy"></div>
         </n-card>
       </div>

         <n-form-item label="期待达到什么效果？">
             <n-input v-model:value="campaignInfo.objectives" type="textarea" clearable size="large" placeholder=""/>
         </n-form-item>

         <n-button v-show="false" @click="createCampaign">确认</n-button>
</n-form>
</template>
<script setup>


import {computed,onBeforeMount,ref,defineEmits,defineProps,defineExpose} from 'vue';
import {  NButton, NForm,NFormItem, NCard, NInput, NSelect,NIcon} from 'naive-ui';
import {useStore} from 'vuex';
import {BulbOutline} from '@vicons/ionicons5';
import MarkdownIt from 'markdown-it';    
//组件挂载前加载数据
onBeforeMount(()=>{
    const store = useStore();
    preData.value = store.getters.temp_campaign_data;
    console.log('预加载数据：',preData.value);
    handleCampaignInfo();
    });
const preData = ref(null);
const campaignInfo = ref({});
const handleCampaignInfo=()=>{
    if(preData.value && JSON.stringify(preData.value)!=='{}' ){
       campaignInfo.value.stage = preData.value.campaignData.stage;
       campaignInfo.value.objectives = preData.value.campaignData.objectives;
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
          label:"1.意识阶段",
          value:"意识阶段",
          //value:"stage0",
          },
      {
          label:"2.兴趣阶段",
          value:"兴趣阶段",
          //value:"stage1",
          },
      {
          label:"3.考虑阶段",
          value:"考虑阶段",
          //value:"stage2",
          },
      {
          label:"4.意向阶段",
          value:"意向阶段",
          //value:"stage3",
          },
      {
          label:"5.行动阶段",
          value:"行动阶段",
          //value:"stage4",
      },
      {
          label:"6.忠诚度建立阶段",
          value:"忠诚度建立阶段",
          //value:"stage5",
          },
      {
          label:"7.推荐阶段",
          value:"推荐阶段",
          //value:"stage6",
          },
      ];
const has_strategy = ref(false);
const campaignStrategy = ref('');
const handleUpdateValue = (value, option) => {
      has_strategy.value = true;
      switch(value){
          case '意识阶段':
              campaignInfo.value.objectives= 
                "建议关注：  \n  客户是否有印象、品牌提及频率、内容查看次数 ";
              campaignStrategy.value =
               "### 意识阶段：客户初识，需要建立起对产品或品牌的初步印象  \n\n  "+
               "**本阶段典型策略举例**——  \n  "+
               "1.利用社群成员分享品牌故事  \n  "+
               "2.强调品牌价值观和创始人IP  \n  3.提供有价值的内容";
          break;
          case '兴趣阶段':
              campaignInfo.value.objectives= 
              "建议关注： \n  客户主动问询次数、客户间交流次数、内容关注度(浏览量)";
              campaignStrategy.value =
              "### 兴趣阶段：激发客户兴趣，增强了解意愿  \n  "+
              "**本阶段典型策略举例**——  \n  "+
              "1.提供深度内容，如使用教程、效果前后对比;  \n  2.社群互动，如问答、讨论;  \n  3.创始人参与讨论"
          break;
          case '考虑阶段':
              campaignInfo.value.objectives=
              "建议关注：用户试用率、用户反馈、产品比较次数";
              campaignStrategy.value =
              "### 考虑阶段：提供决策思路，提升客户购买或相关行动可能性  \n  "+
              "**本阶段典型策略举例** ——  \n  "+
              "1.分享用户评价和案例研究;  \n  2.提供产品试用或样品;  \n  3.强调产品的独特卖点（USP）";
          break;
          case '意向阶段':
              campaignInfo.value.objectives=
              "建议关注：意向用户数量、优惠使用率、用户咨询次数";
              campaignStrategy.value =
              "### 意向阶段：帮助客户下决心，强化购买或相关行动意向  \n  "+
              "**本阶段典型策略举例** ——  \n  "+
              "1.根据用户反馈设计个性化服务;  \n  2.提供社群专属优惠;  \n  3.强调稀缺性，如限量、限时";
          break;
          case '行动阶段':
              campaignInfo.value.objectives=
              "建议关注：转化率、购买数量、平均订单价值";
              campaignStrategy.value =
              "### 行动阶段：提出明确行动方式并号召，促使行动落  \n  "+
              "**本阶段典型策略举例** ——   \n  "+
              "1.设置类似一键购买或快速购买流程;  \n  2.提供清晰的CTA;  \n  3.社群内快速响应";
          break;
          case '忠诚度建立阶段':
              campaignInfo.value.objectives=
              "建议关注：重复购买率、会员活跃度、用户推荐率";
              campaignStrategy.value =
              "### 忠诚度建立阶段：提供优质差异化服务价值，建立客户忠诚度 \n "+
              "**本阶段典型策略举例** ——  \n  "+
              "1.设立会员分层机制;  \n  2.提供定期的用户关怀;  \n  3.收集用户反馈进行产品迭代";
          break;
          case '推荐阶段':
              campaignInfo.value.objectives=
              "建议关注：-新用户增长率、相关推荐数量、社群扩张速度";
              campaignStrategy.value =
              "### 推荐阶段：借助满意度较高的客户实现口碑推荐  \n  "+
              "**本阶段典型策略举例** ——  \n  "+
              "1.设计推荐计划和奖励机制;  \n  2.鼓励用户分享使用体验;  \n  3.利用用户生成内容";
          break;
          default:
              campaignInfo.value.objectives='';
          }
      console.log("value: " + JSON.stringify(value));
      console.log("option: " + JSON.stringify(option));
      };
const md=MarkdownIt()
const markdownStrategy=computed(()=>{
    return md.render(campaignStrategy.value)
    })

const emit = defineEmits(['createdCampaignInfo']);
const createCampaign = () =>{
      console.log('提交营销目标表单信息：',campaignInfo.value);
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
defineExpose({createCampaign,campaignInfo});
defineProps({labelWidth:{default:190}});
</script>
<script>
  export default{
      name:'CreateCampaignForm'
      };
</script>
<style>
.trick{
   margin-bottom:2em;
   text-align:left
    }
.trick .n-icon{
margin-right:5px;
}</style>
