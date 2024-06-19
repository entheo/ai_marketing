<!--DashboradPage.vue-->
<template>
    <n-layout position="absolute">

        <n-layout has-sider>
            <!--侧边导航-->
            <n-layout-sider
                class="siderBar"
                content-style="padding: 20px 20px 0 20px;"
                bordered
                collapse-mode="width"
                :collapsed-width="64"
                :width="200"
                :collapsed="collapsed"
                show-trigger
                @collapse="collapsed = true"
                @expand="collapsed = false">
                    <h1>步步为营</h1>
                    <div :class="{'icon-only': collapsed}">
                    <span class="btnName">v_0.1.0</span>
                    </div>
                
                    <n-flex justify="center">
                        <n-button class="newCopyButton" 
                         :class="{'icon-only': collapsed}"
                         size="large"  strong 
                            @click="toShowGuideModal" type='info'>
                            <n-icon>
                            <create-outline/>
                            </n-icon>
                                <span class="btnName">获得文案灵感</span>
                                </n-button>

                        <n-button class="modifyCopyButton" strong
                            :class="{'icon-only': collapsed}"
                            @click="toShowAdviceModal" 
                            type='info' ghost>
                            <n-icon >
                            <trending-up-outline/>
                            </n-icon>
                                <span class="btnName"> 优化现有文案</span></n-button>
                    </n-flex>
                
                <!--以后用来展示记录
                <n-menu
                    :collapsed="collapsed"
                    :collapsed-width="64"
                    :collapsed-icon-size="22"
                    :options="menuOptions"/>
                -->

            </n-layout-sider>
            
            <!--右侧内容区(包含设置区与生成文案区)-->
            
            <!--名人名言-->
            <n-flex v-show="!showSettingPanel" class="no-content" justify="center">
                <n-card class='quotes' :bordered="false"><famous-quotes/></n-card>
            </n-flex>
            <n-layout-content v-show="showSettingPanel">
                
                <n-split default-size="320px" direction="horizontal" style="height:100%" :native-scrollbar="false">
                    <template #1>
                        <n-layout class="setting-panel" :native-scrollbar="false">
                          <n-layout-header position="absolute">
                            任务设置区
                          </n-layout-header>
                          
                          <n-layout class="setting-panel-content" 
                            content-style="padding: 20px;">   
                            
                            <n-divider>场景&情绪
                              <n-icon><happy-outline/></n-icon>
                            </n-divider>
                            <create-senario-form
                             ref="senarioForm"
                             :label-width="settingLabelWidth"
                             :label-placement="settingPlacement"
                             @senarioInfoCreated="updateSenarioData"/>
                           
                           <n-divider>产品信息
                            <n-icon><cart/></n-icon>
                           </n-divider> 
                           <simple-product-form
                           ref="productForm"
                           :label-width="settingLabelWidth"
                           :label-placement="settingPlacement"
                           @createdProductInfo="updateProductData"/>

                           <n-divider>目标客户信息
                           <n-icon><people/></n-icon>
                           </n-divider>
                           <create-persona-form
                           ref="personaForm"
                           :label-width="settingLabelWidth"
                           :label-placement="settingPlacement"
                           @createdPersonaInfo="updatePersonaData"/>

                           <n-divider>目标效果信息
                           <n-icon>
                           <checkmark-done/>
                           </n-icon></n-divider>
                            <simple-campaign-form
                            ref="campaignForm"
                            :label-width="settingLabelWidth"
                            :label-placement="settingPlacement"
                            @createdCampaignInfo="updateCampaignData"/>
                        </n-layout> 
                        <n-layout-footer class="siderFooter" position="absolute"> 
                          <n-button ghost @click="submitSettingData" 
                              type="primary">
                              生成文案
                              <n-icon size="20">
                              <cafe/>
                              </n-icon>
                              </n-button>
                        </n-layout-footer>
                        </n-layout>
                    </template>
                    
                    <template #2>
                      <n-spin class='wait-response' :show='waitResponse'>
                        <template #description>
                          <n-card :bordered="false">
                            正在分析文案内容...
                          </n-card>
                        </template>
                        <n-layout :native-scrollbar="false" 
                          content-style="padding: 20px;" 
                          :bordered="false">
                        <div v-show="!waitResponse" class="response" 
                          v-html="markdownResponse"/>
                        </n-layout>
                      </n-spin>
                    </template>
                
                </n-split>
            </n-layout-content>
        </n-layout>
     
      
    <!--
      <n-card :title="已创建列表" :bordered="false" v-if="userInfo.created_campaigns">
        <n-card v-for="cam in userInfo.created_campaigns" :key="cam.id || cam" >
          {{cam}}
        </n-card>
      </n-card>
     -->
  


</n-layout>


<n-modal
  v-model:show="showGuideModal"
    :mask-closable="false"
    preset = "card"
    :style="bodyStyle"
    title="输入重要背景信息"
    size="small"
  >
 <guide-page @guideFormData="handleGuideFormData" @response='handleResponse'  :modifyMode="modifyMode"/>
</n-modal>

<!--获得分析建议Modal-->
<n-modal
  v-model:show="showAdviceModal"
    :mask-closable="false"
    preset = "card"
    :style="bodyStyle"
    title="对已有文案进行点评" 
    size="small"
    positive-text="创建" 
    negative-text="取消" >

  <n-layout class='advice-modal'>
    <n-spin :show='waitAdvice'>
      <template #description>
        <n-card :bordered="false">正在分析文案内容...</n-card>
      </template>
    
      <n-layout content-style="padding:20px;">
        <input-copy-form @copyOriginalInfo="getAdvices" ref="copyForm" :bordered="false"/>
        <div class="center_bu">
          <n-button type="Primary" @click="handleCopyOriginalInfo">获取分析&建议
          </n-button>
        </div>
      </n-layout>
    </n-spin>
      
    <n-layout class="advice-response" v-show="hasAdvice" content-style="padding: 20px">
      <n-layout class='advice-content' 
        :native-scrollbar="false" content-style="height:300px">
        <div v-html="markdownAdviceResponse" />
      </n-layout>
      <n-layout-footer class="center_bu">
          <n-button v-show='hasAdvice' type="info" 
            @click='toSettingForm'>获取新的文案灵感
            <n-icon><caret-forward-circle-outline/></n-icon>
          </n-button>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</n-modal>

</template>


<script setup>
import GuidePage from './GuidePage.vue';
//import { isYesterday, addDays } from 'date-fns/esm';
//import {NForm,NFormItem,NInput} from 'naive-ui';
import {NModal, NButton, NLayout,NSpin,NLayoutContent,NLayoutHeader,NLayoutFooter,NCard} from 'naive-ui';
import {NIcon,NDivider,NFlex,NSplit,NLayoutSider} from 'naive-ui';
//import {NMenu} from 'naive-ui';
import MarkdownIt from 'markdown-it';
import {computed} from 'vue';
import {ref} from 'vue';
import axios from 'axios';
import {onBeforeMount} from 'vue';
import InputCopyForm from './InputCopyForm.vue'; 
import {useStore} from 'vuex';
import {useRouter} from 'vue-router';
import FamousQuotes from './FamousQuotes.vue';

//导入图标
import {CaretForwardCircleOutline,TrendingUpOutline,Cafe,People,CheckmarkDone,CreateOutline,HappyOutline,Cart} from '@vicons/ionicons5';

//导入表单组件
import CreateSenarioForm from './CreateSenarioForm.vue';
import SimpleProductForm from './SimpleProductForm.vue';
import CreatePersonaForm from './CreatePersonaForm.vue';
import SimpleCampaignForm from './SimpleCampaignForm.vue';

const userName = ref('');
const userInfo = ref({
    username:'',
    created_brands:'',
    created_campaigns:'',
    created_products:'',
    });

//定义预先加载的设置数据
const preSettingData=ref({});
//定义用户信息
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
        userInfo.value = resp.data;
        userName.value = resp.data.username;
        //has_brands.value = resp.data.created_brands.length;
        localStorage.setItem('username',resp.data.username);
          } catch (error) {
          if(error.response && error.response.status==401){
              router.push('/');}
          console.error('Failed to fetch user info:', error);
      }
    };
const bodyStyle = ref({
  width: "800px"
});

//侧边导航记录
/*
const menuOptions = [
  {
      label:"菜单一",
      key:"menu1",
      href:"/"
    },
  {
      label:"菜单2",
      key:"menu2",
      href:"/"
      }
];
*/

//触发子组件的保存按钮，继而触发emit
const copyForm = ref(null);
const handleCopyOriginalInfo = () =>{ 
    waitAdvice.value=true;
    copyForm.value.updateCopyOriginal();
    };  


/*将原文与营销背景一起发送后台寻求建议
const showCampaignBackgroundModalRef = ref(null);
const showCampaignBackgroundModal = showCampaignBackgroundModalRef;
//用prompt存储原文以及营销背景信息
const prompt = ref({});
const saveOriginalInfo = (message)=>{
    showCampaignBackgroundModal.value = true;
    prompt.value.originall = message;
    console.log(prompt.value);
    }
*/

//解析Markdown格式
const md = MarkdownIt();


//调用GuidePage创建新文案
const showGuideModal=ref(false);
const toShowGuideModal=()=>{
    fetchUserInfo().then(
    showGuideModal.value=true);
    //showGuideModal.value=true
    }
//处理GuidePage emit来的数据
const response=ref('');
const markdownResponse = computed(()=>{
    console.log(response.value);
    return md.render(response.value)});
const handleResponse=(message)=>{
    console.log(message)
    response.value=message;
    };
const showSettingPanel=ref(false);
const handleGuideFormData=(message)=>{
    //关闭GuideModal
    showGuideModal.value=false;
    showSettingPanel.value=true;
    console.log(message);
    preSettingData.value=message;
    updateSettingForm().then(
     submitSettingData());
    };

const updateSettingForm = async()=>{
   //同步场景表单
   if(senarioForm.value.places.some(item=>item.label!==preSettingData.value.senarioData.places)){
        senarioForm.value.otherPlace=true;
        senarioForm.value.otherPlaceData=preSettingData.value.senarioData.places;
        }
   senarioForm.value.senarioInfo = preSettingData.value.senarioData;
   //senarioForm.value.createSenario();
   //同步产品信息表单
   productForm.value.productInfo = preSettingData.value.productData;
   //productForm.value.createProduct();
   //同步客户画像表单
   personaForm.value.personaInfo = preSettingData.value.personaData;
   //personaForm.value.createPersona();
   //同步营销目标表单
   campaignForm.value.campaignInfo = preSettingData.value.campaignData;
   //campaignForm.value.createCampaign();
    };

//将原文发往后台获得建议
const adviceResponse = ref(null);
const waitAdvice = ref(false);
const hasAdvice = ref(false);
const promptData = ref({});

//解析Markdown格式
const adviceTextRef = ref('');
const markdownAdviceResponse = computed(()=>{
    console.log(adviceTextRef.value);
    return md.render(adviceTextRef.value)});
const token = localStorage.getItem('token');

//触发显示AdviceModal
const showAdviceModal = ref(false);
const toShowAdviceModal = () => {
    fetchUserInfo().then(
        showAdviceModal.value=true
       )} 
//向发起后台请求
const getAdvices = async(message) => {
    adviceResponse.value={};
    promptData.value.original=message;
    //showAdviceModal.value=true;
    promptData.value.type='advice';
    await axios.post("/api/advice/",promptData.value,{
            headers:{
                'Authorization':`Bearer ${token}`,
                },
            withCredentials:true,
                }).then(resp_json => {
                   // 处理你后端返回的response
                   hasAdvice.value=true;
                   console.log(hasAdvice.value);
                   waitAdvice.value=false;
                   //adviceTextRef.value=resp_json.data
                   console.log(resp_json.data);
                   adviceResponse.value=resp_json.data;
                   adviceTextRef.value = formatAdviceText();
                 })
                .catch(err => {
            console.log('Fail to get info:',err);
            });
    
    };

//格式化后台字段
const formatAdviceText = () =>{
   
    const campaignBackground = adviceResponse.value.campaignData;
    const persona = adviceResponse.value.personaData;
    const product = adviceResponse.value.productData;
    const senario = adviceResponse.value.senarioData;
    const advices = adviceResponse.value.advicesData;
    return `# 相关营销背景的推测：\n\n## 营销目标\n **目前可能所处营销阶段**：\n${campaignBackground.stage}\n**该阶段主要参考效果目标**：\n ${campaignBackground.objectives}\n\n ## 目标受众画像\n **主要群体** ：\n ${persona.motives}\n\n  ## 关于产品与品牌\n **独特卖点(USP)**：\n${product.usp} \n\n**品牌理念**:\n ${product.values} \n\n ## 关于营销场景与情绪\n **文案体现出的主要情绪**：\n ${senario.emotionTags}\n **适合使用的地方**：\n${senario.places} \n\n ##一些供参考的优化建议：${advices}`
    } 

//跳转CampaignPage继续获取优化后的文案
const store = useStore();
const router = useRouter();

const toSettingForm = ()=>{
    //添加原文
    adviceResponse.value.original = promptData.value.original;
    preSettingData.value = promptData.value
    console.log()
    console.log(typeof(adviceResponse.value));
    //store.commit('set_temp_campaign_data',adviceResponse.value);
    console.log(store.getters.temp_campaign_data);
    showSettingPanel.value=true;
    preSettingData.value=adviceResponse.value;
    
    updateSettingForm().then(
     submitSettingData()).then(showAdviceModal.value=false);
    }

//获取任务建议
/*const taskInfo = ref('');
const taskResponse = ref('');
const sendTask = async() => {
    await axios.post("/api/advice/",taskInfo.value,{
            headers:{
                'Authorization':`Bearer ${token}`,
                },
            withCredentials:true,
                }).then(resp => {
                   // 处理你后端返回的response
                   console.log(typeof(resp.data));
                   taskResponse.value = resp.data;
                 })
                .catch(err => {
            console.log('Fail to get info:',err);
            });
   
    }

const markdownTaskResponse = computed(()=>{
    return md.render(taskResponse.value)});
*/

//定义表单组件
const senarioForm=ref(null);
const productForm=ref(null);
const personaForm=ref(null);
const campaignForm=ref(null);

//表单组件方法
const settingLabelWidth=ref('100');
const settingPlacement=ref('top');
const settingFormData=ref({});
const updateProductData = (message) => {
    console.log('Update Product');
    settingFormData.value.productData = message;
    console.log('已填产品信息:',settingFormData.value);
    };
const updateSenarioData = (message) =>{
    console.log('Update Senario');
    settingFormData.value.senarioData = message;
    console.log('已填场景信息:',settingFormData.value);
    };
const updateCampaignData = (message) =>{ 
    console.log('Update Campaign');
    settingFormData.value.campaignData = message;
    console.log('已填营销目标信息:',settingFormData.value);
    };
const updatePersonaData = (message) =>{ 
    console.log('Update Persona');
    settingFormData.value.personaData = message;
    console.log('已填场景信息:',settingFormData.value);
    };
const getCsrfToken = () => {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken'))
    ?.split('=')[1];
};
//批量保存表单组件信息
const saveForms = () =>{
   senarioForm.value.createSenario();
   productForm.value.createProduct();
   personaForm.value.createPersona();
   campaignForm.value.createCampaign();
   console.log('最终设置信息:',settingFormData.value);
    };
const waitResponse = ref(false)
const submitSettingData = async()=>{
   waitResponse.value=true;
   //保存表单组件信息
   saveForms();
   //请求后台
   const csrfToken= ref(getCsrfToken());
   settingFormData.value.type='new_copy';
   try{
       const resp =  await axios.post('/api/response/',settingFormData.value,{
           headers: {
                'Authorization': `Bearer ${token}`, // 设置请求头
                'X-CSRFToken': csrfToken.value,
                },  
           withCredentials: true,});
           console.log(resp);
           response.value=resp.data.message;
           waitResponse.value=false;
           }catch (error) {
        console.error('Failed to get info:', error);
        }
        }   



onBeforeMount(()=>{
    fetchUserInfo();})

//定义样式
const collapsed=ref(false)
</script>

<style>
.n-layout{
    height:100%}

.center_bu{
    display:flex;
    align-items:center;
    justify-content:center;
    }

.response{
    text-align:left;}

.n-card__content {
    padding:0px 14px 0px 0px}

.newCopyButton ,.modifyCopyButton{
    width:150px;
    }
.newCopyButton{
    height:50px;
    border-radius:5px;
    margin-bottom:20px;
    margin-top:20px;
    }
.newCopyButton .n-icon,.modifyCopyButton .n-icon,siderFooter .n-icon{
    font-size:20px;
    margin-right: 5px;
    height:auto;
    min-width: 20px;}

.icon-only {
  width: 45px !important;
  height: 45px !important;
}
.icon-only .n-icon{
    font-size:24px;
    margin-left: -5px;
    margin-top:2px;}
.icon-only .btnName {
  display: none;
}
.n-divider .n-icon{
    font-size: 20px;
    margin-left: 5px;
    height: auto;}
.siderBar{
    background-color:#f4f4f6;
    }
.setting-panel{
    background-color:#f9f9f9;}
.setting-panel-content{
    margin-bottom:30px}
.siderFooter{
    background-color:white;
    width: 100%;
    z-index:1000;
    height:60px;
    }
.siderFooter .n-button{
    z-index:1000;
    width:93%;
    margin-top:10px}
.no-content {
    flex-direction:column;
    font-size:40px;
    width:100%;
    align-items:center;}
.advice-modal{
    text-align:center}
.advice-content{
    text-align:left
    }
.advice-response .n-layout-footer{
    background:white;}
.wait-response{
    height:100%}
</style>
