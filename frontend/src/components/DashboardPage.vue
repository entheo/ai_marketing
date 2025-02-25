<!--DashboradPage.vue-->
<template>

<!---------------------------布局为左右分部，右侧都嵌套在n-layout中--------------------->
<n-layout position="absolute">
      <n-layout has-sider>

        <!--侧边导航-->
          <n-layout-sider
                class="siderBar"
                content-style="overflow:hidden;padding: 20px 20px 0 20px;"
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

                    <!--左侧操作按钮-->
                    <n-flex class='sider-btns' justify="center">
                        <n-button 
                         v-show="false"
                         class="newCopyButton" 
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
                            :disabled="waitAdvice"
                            @click="toShowAdviceModal" 
                            type='info' ghost>
                            <n-icon >
                              <trending-up-outline/>
                            </n-icon>
                            <span class="btnName"> 用文章解密市场</span>
                        </n-button>
                        
                        <n-button class="modifyCopyButton" strong
                            :class="{'icon-only':collapsed}"
                            :disabled="waitAdvice"
                            @click="toShowRednoteModal"
                            type='info' ghost>
                            <n-icon><trending-up-outline/></n-icon>
                            <span class="btnName">小红书账号评分</span>
                        </n-button>
                              

                        <n-button quaternary class="show-contact"
                          :class="{'icon-only':collapsed}"
                          type = 'info'
                          @click="showContactModal=true">
                          <span class="btnName">
                            联系作者
                          </span>
                          <n-icon><chatbubbles-outline/></n-icon>
                        </n-button>
                    
                    </n-flex>
            </n-layout-sider>
            
            
            <!--右侧内容区(包含设置区与生成文案区)-->
           
            <!--名人名言区域-->
            <n-flex v-show="showQuotes" class="no-content" justify="center">
            <!--n-flex v-show='false'-->
                <n-card class='quotes' :bordered="false"><famous-quotes/></n-card>
            </n-flex>

            <!--设置信息区域--> 
           <n-layout v-show="showSettingPanel">
           <n-layout-content>
              <n-split default-size="560px" direction="horizontal" style="height:100%" :native-scrollbar="false">
                <template #1>
                  <n-layout class="setting-panel" :native-scrollbar="false">
                          <n-layout-header position="absolute">
                            任务设置区
                          </n-layout-header>
                           
                          <n-layout class="setting-panel-content" 
                            content-style="padding: 20px;">   
                           
                           <!--产品与客户区域-->
                            <n-flex inline='true' justify="space-around" class='product-persona'>
                              <n-card :title=settingFormData.productData.name
                               :bordered='false' embedded class='product'>
                                <template #header-extra>
                                  <n-icon>
                                   <create-outline/>
                                  </n-icon>
                                </template>
                                <div><b>理念</b>：{{settingFormData.productData.brandValues}}</div>
                                <div><b>卖点</b>：
                                {{settingFormData.productData.usp}}
                                  </div>
                              </n-card>
                              <n-card :title=settingFormData.personaData.desc :bordered='false' embedded class='persona'>
                                <template #header-extra>
                                  <n-icon>
                                    <create-outline/>
                                  </n-icon>
                                </template>

                                <div><b>收入</b>：{{settingFormData.personaData.salary}}</div>
                                <div><b>诉求</b>：
                                {{settingFormData.personaData.motives}}
                                </div>
                              </n-card>
                            </n-flex>
                           

                            <n-divider>设定目标
                              <n-icon>
                                <checkmark-done/>
                              </n-icon>
                            </n-divider>
                            <simple-campaign-form
                            ref="campaignForm"
                            :label-width="settingLabelWidth"
                            :label-placement="settingPlacement"
                            @createdCampaignInfo="updateCampaignData"/>
                           
                            <n-divider>选择场景
                            <n-icon><happy-outline/></n-icon>
                            </n-divider>
                            <create-senario-form
                             ref="senarioForm"
                             :label-width="settingLabelWidth"
                             :label-placement="settingPlacement"
                             @senarioInfoCreated="updateSenarioData"/>
                           
                           
                           <!--n-divider>产品信息
                           <n-icon><cart/></n-icon>
                           </n-divider--> 
                           <simple-product-form
                           v-show='false'
                           ref="productForm"
                           :label-width="settingLabelWidth"
                           :label-placement="settingPlacement"
                           @createdProductInfo="updateProductData"/>

                           <n-divider>目标客户信息
                           <n-icon><people/></n-icon>
                           </n-divider>
                           <create-persona-form
                           v-show='false'
                           ref="personaForm"
                           :label-width="settingLabelWidth"
                           :label-placement="settingPlacement"
                           @createdPersonaInfo="updatePersonaData"/>
                        
                        </n-layout> 
                        <n-layout-footer class="siderFooter" position="absolute"> 
                          <n-button  @click="submitSettingData" 
                              type="info">
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

            <!----------------获取建议模式----------------->
            <n-layout v-show="showAdviceMode">
              <n-split default-size="30%" direction="horizontal" style="height:100%" :native-scrollbar="false">
                
                <!--原文展示区-->
                <template #1>
                  <n-layout content-style="padding:20px" class="content-panel setting-panel" :native-scrollbar="false">
                    <div v-html="markdownOriginal"/>
                  </n-layout>
                </template>
          
                <!--建议展示区-->
                <template #2>
                  <n-layout>

                    <!--建议内容-->
                    <n-layout-content content-style="padding: 20px;" class="content-panel" :native-scrollbar="false">
                      <div v-html='markdownAdviceResponse' ref='textToCopy'/>
                    </n-layout-content>

                    <!----底部提示---->
                    <n-layout-footer class="copy-text" position="absolute">
                      <n-flex justify="center">
                        <span>以上内容不会自动保存，会在页面刷新后消失</span>
                        <n-button @click="copyText">复制</n-button>
                      </n-flex>
                    </n-layout-footer>
                
                  </n-layout>
                </template>
              
              </n-split>
            </n-layout>
      
    
    </n-layout>
    <!-- （未启动）
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

<!--输入小红书账号信息-->
<n-modal
  v-model:show="showRednoteModal"
  :mask-closable="false"
  preset="card"
  :style="bodyStyle"
  title="测测你的小红书账号名称能打多少分？"
  size="small"
  :block-scroll="false">
  
  <n-layout class='advice-modal'>
    <n-spin :show='waitAdvice'>
      <template #description>
        <n-card :bordered="false">正在分析文案内容...</n-card>
      </template>
      
      <n-layout content-style="padding:20px;">
        <input-rednote-info @accountInfo="getAdvices" ref="redNoteForm" bordered="false"/>
        <div class="center_bu">
          <n-button type="Primary" @click="handleRednoteInfo">开始打分</n-button>
        </div>
      </n-layout>
    
    </n-spin>
  </n-layout>
</n-modal>

<!--获得文章分析建议Modal-->
<n-modal
  v-model:show="showAdviceModal"
    :mask-closable="false"
    preset = "card"
    :style="bodyStyle"
    title="粘贴已有文章，反推市场策略" 
    size="small"
    positive-text="创建" 
    negative-text="取消" 
    :block-scroll="false"
    >
  <!--粘贴文章-->
  <n-layout class='advice-modal'>
    <n-spin :show='waitAdvice'>
      <template #description>
        <n-card :bordered="false">正在分析文案内容...</n-card>
      </template>
    
      <n-layout content-style="padding:20px;">
        <input-copy-form @copyOriginalInfo="getAdvices" ref="copyForm" :bordered="false"/>
        <div class="center_bu">
          <n-button type="Primary" @click="handleCopyOriginalInfo">获取分析建议
          </n-button>
        </div>
      </n-layout>
    </n-spin>
     
    <!----未启动----> 
    <n-layout class="advice-response" v-show="hasAdvice" content-style="padding: 20px" :native-scrollbar="false">
      <n-layout-content class='advice-content' 
        :native-scrollbar="false" content-style="height:300px">
        <div v-html="markdownAdviceResponse" />
      </n-layout-content>
      <n-layout-footer class="center_bu">
        <n-button v-show='hasAdvice' type="info" 
          @click='toSettingForm'>获取新的文案灵感
            <n-icon><caret-forward-circle-outline/></n-icon>
        </n-button>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</n-modal>

<!--联系作者-->
<n-modal v-model:show="showContactModal">
  <n-card class='contact'>
    <template #cover>
      <img src="./images/contact.jpg"/>
    </template>
    你好，欢迎添加我的企业微信
  </n-card>
</n-modal>

</template>


<script setup>
import GuidePage from './GuidePage.vue';
import {NModal, NButton, NLayout,NSpin,NLayoutContent,NLayoutHeader,NLayoutFooter,NCard} from 'naive-ui';
import {useNotification,NIcon,NDivider,NFlex,NSplit,NLayoutSider} from 'naive-ui';
import MarkdownIt from 'markdown-it';
import {computed} from 'vue';
import {ref} from 'vue';
import axios from 'axios';
import {onBeforeMount,onMounted,onBeforeUnmount} from 'vue';
import {useStore} from 'vuex';
import {useRouter} from 'vue-router';
import FamousQuotes from './FamousQuotes.vue';
import Clipboard from 'clipboard';

//导入图标
import {CaretForwardCircleOutline,ChatbubblesOutline,TrendingUpOutline,Cafe,CheckmarkDone,CreateOutline,HappyOutline} from '@vicons/ionicons5';

//导入表单组件
import CreateSenarioForm from './CreateSenarioForm.vue';
import SimpleProductForm from './SimpleProductForm.vue';
import CreatePersonaForm from './CreatePersonaForm.vue';
import SimpleCampaignForm from './SimpleCampaignForm.vue';
import InputCopyForm from './InputCopyForm.vue';
import InputRednoteInfo from './InputRednoteInfo.vue';


const showContactModal=ref(false);
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
      //console.log(token);
      try {
        const resp =  await axios.get('/account/auth/',{
            headers: {
                'Authorization': `Bearer ${token}` // 设置请求头
                }});
        console.log('验证结果:')
        console.log(resp.data.auth);
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

const showQuotes=ref(true);
//填写文章时触发InputCopyForm组件
//触发子组件的保存按钮，继而触发emit
const copyForm = ref(null);
//触发子组件copyForm的更新=>触发getAdvices方法
const handleCopyOriginalInfo = () =>{ 
    waitAdvice.value=true;
    copyForm.value.updateCopyOriginal();
    };  

//填写小红书账号信息是触发
const redNoteForm = ref(null);
const handleRednoteInfo = () =>{
    waitAdvice.value = true;
    redNoteForm.value.updateRednoteInfo();
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
    showQuotes.value=false;
    console.log(message);
    preSettingData.value=message;
    updateSettingForm().then(
     submitSettingData()).then(
     collapsed.value=true)};
    

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
    //console.log(adviceTextRef.value);
    return md.render(adviceTextRef.value)});
const originalTextRef=ref('');
const markdownOriginal=computed(()=>{
    return md.render(originalTextRef.value)
    });
const token = localStorage.getItem('token');

//触发显示粘贴文章输入框AdviceModal
const showAdviceModal = ref(false);
const toShowAdviceModal = () => {
    fetchUserInfo().then(
        showAdviceModal.value=true
       )} 
const showAdviceMode = ref(false);

//触发显示小红书账号输入框
const showRednoteModal = ref(false);
const toShowRednoteModal = () => {
    fetchUserInfo().then(
        showRednoteModal.value=true
        )}
//向发起后台请求
const getAdvices = async(message) => {
    console.log(message);
    console.log('message 类型:', typeof message);
    adviceResponse.value={};
    switch(true){
      case (message.type=='article'):
        promptData.value.original=message.info;
        break;
      case (message.type=='rednote'):
        promptData.value.original='';
        promptData.value.name=message.name;
        promptData.value.intro=message.intro;
        break;
      default:
        console.log('没有获取数据')
    }
    promptData.value.type = message.type;
    console.log(promptData.value);
    await axios.post("/api/advice/",promptData.value,{
           timeout:50000,
           headers:{
                'Authorization':`Bearer ${token}`,
                },
            withCredentials:true,
                }).then(resp_json => {
                   // 处理你后端返回的response
                   showAdviceMode.value=true;
                   hasAdvice.value=false;
                   waitAdvice.value=false;
                   //adviceTextRef.value=resp_json.data
                   console.log(resp_json.data);
                   adviceResponse.value=resp_json.data;
                   showQuotes.value=false;
                   if(resp_json.data.adviceType=='article'){
                       originalTextRef.value='# 原文： \n\n'+message.info;
                       adviceTextRef.value=formatArticleAdviceText()
                       showAdviceModal.value=false}
                   else if(resp_json.data.adviceType == 'rednote'){
                       originalTextRef.value = '# 账号信息：\n\n'+'## '+resp_json.data.accountName+'\n\n'+resp_json.data.accountIntro;
                       adviceTextRef.value=formatRednoteAdviceText();
                       showRednoteModal.value=false}
                 })
                .catch(err => {
            waitAdvice.value=false;
            console.log('Fail to get info:',err);
            console.log(err.code);
            const errInfo=ref('');
            switch(err.code){
                case 'ERR_BAD_REQUEST':
                errInfo.value='服务器连接错误,请联系管理员';
                break;
                case 'ECONNABORTED':
                errInfo.value='连接超时，请稍后再试'
                break;
                default:
                errInfo.value='';
                }
            notification.info({
                    content:errInfo.value,
                    duration:4000})
            });
    };


const showDictItems = (dict) => {
    var result = dict
    if(typeof dict == 'object'){
    // 将字典的每一项转换为字符串，并逐行展示
    result = Object.entries(dict)
        .map(([key, value]) => `**【${key}】** ${value}`)
        .join('\n');}
        
    return result; 
};
//格式化后的小红书反馈
const formatRednoteAdviceText = ()=>{
    const rating = adviceResponse.value.rating;
    const persona = adviceResponse.value.persona;
    const name = adviceResponse.value.name;
    const clear = name.clear;
    const intro = adviceResponse.value.intro;
    const avatar = adviceResponse.value.avatar;
    const usertagArray = persona.usertags;
    const usertags = usertagArray.map((usertag)=>{
        return `${usertag} `}).join(' ');
    return `# 评估与建议：
## 得分—— ${rating.number}/100 
【评语】${rating.summary} \n\n
## 受众画像(推测)：
- **Ta们是谁？** \n
    ${persona.des} \n
- **用户故事**  \n
    ${persona.userstory} \n

- **典型标签**  \n
    ${usertags} \n\n

## 名称分析：
- **定位** \n
    ${showDictItems(clear)} \n

- **传播难度** \n
    ${showDictItems(name.easy)} \n

- 用户吸引力 \n
    ${showDictItems(name.popular)}
    
- **差异化竞争力** \n
    ${showDictItems(name.diff)}

- **SEO组合策略** \n
    ${showDictItems(name.seo)}

- **合规与延展性 \n
    ${showDictItems(name.safe)}

- **情感共鸣度** \n
    ${showDictItems(name.emotional)}

## 简介分析：
${showDictItems(intro)}

## 头像建议：
${avatar.better} \n\n
`;
    }

//格式化后的文章类字段
const formatArticleAdviceText = () =>{
   
    const campaignBackground = adviceResponse.value.campaignData;
    const persona = adviceResponse.value.personaData;
    const product = adviceResponse.value.productData;
    const senario = adviceResponse.value.senarioData;
    const advicesArray = adviceResponse.value.advicesData;
    const advices = advicesArray.map((advice,index)=>{
        return `
        ${index+1}.${advice.issue}   
        建议：${advice.suggestion}`
        }).join('\n');

    return `# 分析与建议：

## 关于产品——
- **主推产品名称？** \n
  ${product.name}
- **是否包含独特卖点(USP)的相关信息？**  \n  
  ${product.has_usp} 。${product.usp}  \n
- **是否有提倡的品牌理念**?  \n  
  ${product.has_brandValues}。${product.brandValues}  \n\n 

## 关于客户——
- **目标群体可能是谁？**  \n 
  ${persona.desc}。${persona.p_reason}  \n
- **相关心理诉求是什么 ？**  \n
  ${persona.motives}  \n\n  

## 关于目标——
- **可能所处营销阶段** ：${campaignBackground.stage}。  \n  
  因为${campaignBackground.c_reason}。  \n  
- **该阶段主要的参考目标是什么**？  \n  
  ${campaignBackground.objectives}  \n\n  

## 关于场景——
- **与目前阶段匹配的场景是哪里**?  \n  
  ${senario.places}  \n  
- **原文传递出了哪些主要情绪**？  \n  
  ${senario.emotionTags}  \n  
- **是否合适**？  \n  
  ${senario.e_reason}  \n\n

## 相关优化建议——  \n  
${advices}  
`;
}

//复制分析建议
const textToCopy=ref(null);

/* navigator.clipboard方法，因无https暂停用
const copyText = async()=>{
    console.log(textToCopy)        
    if(!textToCopy.value) 
        return;
    try{
        if(navigator.clipboard && navigator.clipboard.writeText){
        console.log('Attempting to write text to clipboard');
        await navigator.clipboard.writeText(textToCopy.value.textContent);
        notification.success({
            content:"已成功复制到粘贴板",
            duration:2500})
        }else{
            console.error('Clipboard API not supported or writeText not available');
            }

        }catch(err){
        console.log('Error during clipboard operation:',err)}
    
    };*/

let clipboard=null;
const initClipboard = () => {
  if (clipboard) {
    clipboard.destroy();
  }};

clipboard = new Clipboard('.copy-text button', {
    text: () => textToCopy.value.innerText || textToCopy.value.textContent
  });

clipboard.on('success', (e) => {
    notification.success({
      content: "已成功复制到粘贴板",
      duration: 2500
    });
    console.log('文本已成功复制到剪贴板');
    e.clearSelection();
  });

  
clipboard.on('error', (e) => {
    console.error('复制到剪贴板操作失败:', e);
  });

const copyText = () => {
  if (!clipboard) { 
    initClipboard();
  }
  // 触发复制操作
  clipboard.onClick({ currentTarget: document.querySelector('.copy-text button') });
};

const notification=useNotification();

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
const settingFormData=ref({
    'productData':'',
    'personaData':''});
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
        };   


onBeforeUnmount(() => {
   if (clipboard) {
     clipboard.destroy();
   }
});

onMounted(() => {
  document.tilte="步步为营"
  // Ensure Clipboard is initialized on mount to avoid multiple bindings
  initClipboard();
});

onBeforeMount(()=>{
    fetchUserInfo();})

//定义样式
const collapsed=ref(false);
</script>

<style>
.sider-btns{
    margin-top:40px}
.contact{
    max-width:300px;
    text-align:center}
.contact .n-card__content{
    padding-top:10px}
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
.siderBar .n-layout-sider-scroll-container{
    overflow:hidden}
.setting-panel .setting-panel-content{
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
    width:100%;
    height:100%;
    margin-top:0}
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
.product-persona .n-card {
    width:48%;}
.product-persona h3{
    margin-top:5px}
.product-persona{
    text-align:left;
    }
.product-persona .n-card--embedded{
    background:rgb(240 240 245)}
.product-persona .n-card-header{
    margin-left:0;}
.content-panel{
    text-align:left;}
pre{
    white-space:pre-wrap;
    }
.n-split-pane-2 .content-panel{
    padding-bottom:60px;
    }
.copy-text{
    height:60px;
    padding-top:15px}
.copy-text .n-flex{
    align-items:center}
</style>
