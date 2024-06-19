<!--GuidePage-->

<template>
  <n-spin :show="showSpin">
       <template #description>
           请稍等，正在完成文案任务...
  
      </template>
  
  <n-space class="guide" vertical>
    <n-steps :current="Number(current)" :status="currentStatus">
    
      <n-step
        title="描述产品信息"
        description="好的产品描述不仅能够激发客户的购买欲望，还能建立与客
户之间的情感联系"
      />

      <n-step
        title="定位目标客户"
        description="准确的目标客户画像会让文案更具有针对性与感染力，产生“说到心里”的效果"
      />

      <n-step
        title="分辨营销阶段"
        description="清晰的营销目标不仅增强文案效果的落地性，还能为持续优化营销效果提供重要参考依据。"
      />
      
       <n-step
        title="选择场景&情绪"
        description="选择合适的营销场景，并匹配相符的情绪，可以有效地推动
目标客户采取行动"
      />

    </n-steps>
    
    
    <!--
    <n-space>
      <n-button-group>
        <n-button @click="prev">
          <template #icon>
            <n-icon>
              <md-arrow-round-back />
            </n-icon>
          </template>
        </n-button>
        <n-button @click="next">
          <template #icon>
            <n-icon>
              <md-arrow-round-forward />
            </n-icon>
          </template>
        </n-button>
      </n-button-group>
      <n-radio-group v-model:value="currentStatus" size="medium" name="basic">
        <n-radio-button value="error">
          Error
        </n-radio-button>
        <n-radio-button value="process">
          Process
        </n-radio-button>
        <n-radio-button value="wait">
          Wait
        </n-radio-button>
        <n-radio-button value="finish">
          Finish
        </n-radio-button>
      </n-radio-group>
    </n-space>
  -->
</n-space>

<!--产品信息-->
<n-card :bordered="false" v-show="currentRef==1">
    <simple-product-form :label-width="guideLabelWidth" @createdProductInfo = "updateProductData" ref="productForm"/>
    <n-flex justify="center">
        <n-button type="info" @click="saveProductForm">保存，下一步</n-button>
    </n-flex>
</n-card>

<!--场景&情绪-->
<n-card :bordered="false" v-show="currentRef==4">
    <create-senario-form :label-width="guideLabelWidth" :campaignStage="campaignDataStage" @senarioInfoCreated="updateSenarioData" ref="senarioForm"/>
    <n-flex justify="center">
        <n-button @click="prev">上一步</n-button>
        <!--n-button type="info" @click="saveSenarioForm">保存，下一步</n-button-->
        <n-button type="primary" @click="submitGuideForm">保存，获取灵感</n-button>
    </n-flex>
</n-card>


<!--受众画像-->
<n-card :bordered="false" v-show="currentRef==2">
    <create-persona-form :label-width="guideLabelWidth" @createdPersonaInfo="updatePersonaData" ref="personaForm"/>
    <n-flex justify="center">
        <n-button @click="prev">上一步</n-button>
        <n-button type="info" @click="savePersonaForm">保存，下一步</n-button>
    </n-flex>
</n-card>

<!--营销目标-->
<n-card :bordered="false" v-show="currentRef==3">
    <simple-campaign-form :label-width="guideLabelWidth" @createdCampaignInfo="updateCampaignData" ref="campaignForm"/>

    <n-flex justify="center">
        <n-button @click="prev">上一步</n-button>
        <n-button type="primary" @click="saveCampaignForm">保存，下一步</n-button>
    </n-flex>
</n-card>
</n-spin>
</template>

<script setup>
import {useStore} from 'vuex';
import {ref,defineProps,watch,defineEmits} from 'vue';
import axios from 'axios';
//import { MdArrowRoundBack, MdArrowRoundForward } from '@vicons/ionicons4';
import {NSpin, NFlex, NCard,  NStep, NSpace, NButton,NSteps} from 'naive-ui';
//import CreateCampaignForm from './CreateCampaignForm.vue';
import SimpleCampaignForm from './SimpleCampaignForm.vue';
import CreatePersonaForm from './CreatePersonaForm.vue';
//import CreateProductForm from './CreateProductForm.vue';
import SimpleProductForm from './SimpleProductForm.vue';
import CreateSenarioForm from './CreateSenarioForm.vue';

const getCsrfToken = () => {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken'))
    ?.split('=')[1];
};
const guideLabelWidth=ref('195');
const props = defineProps({
    modifyMode:Boolean,
    });

 watch(() => props.modifyMode, (newValue) => {
  console.log(newValue); // 应该在 DashboardPage 更新后输出 true
},{
    immediate: true
    },
);

const formData = ref({
    campaignData:null,
    personaData:null,
    productData:null,
    senarioData:null
    });
const currentRef = ref(1);
const currentStatus = ref('process');
const current = currentRef;
const next = () => {
  console.log(currentRef.value);
  if (currentRef.value === null)
    currentRef.value = 1;
  else if (currentRef.value >= 4)
    currentRef.value =4 ;
  else
    currentRef.value++;
 console.log(currentRef.value);
}

const prev = () => {
  console.log(currentRef.value);
  if (currentRef.value === 0)
    currentRef.value = null ;
  else if (currentRef.value === null)
    currentRef.value = 4;
  else
    currentRef.value--;
    if (currentRef.value <1)
        currentRef.value =1;
  console.log(currentRef.value);
};
/*
const campaignForm = ref(null);
const campaignDataStage=ref('123');
const saveCampaignForm = () =>{
    campaignForm.value.createCampaign();   
    }
const updateCampaignData = (message) => {
    console.log('Update Campaign');
    formData.value.campaignData = message;
    console.log(formData.value);
    campaignDataStage = formData.value.campaignData.stage;
    console.log(campaignDataStage);
    next();
    };
*/
//画像表单
const personaForm = ref(null);
const savePersonaForm = () => {
    personaForm.value.createPersona();
    }
const updatePersonaData = (message) => {
    console.log('Update Persona');
    formData.value.personaData = message;
    console.log(formData);
    console.log('已填客户画像:',formData);
    next();
    };

//产品表单
const productForm = ref(null);
const saveProductForm = () => {
    productForm.value.createProduct();
    }
const updateProductData = (message) => {
    console.log('Update Product');
    formData.value.productData = message;
    console.log('已填产品信息:',formData.value);
    next();
    };

//场景情绪表单
const senarioForm = ref(null);
const saveCampaignForm = () => {
    campaignForm.value.createCampaign();}
const updateSenarioData = (message) => {
    console.log('Update Senario');
    formData.value.senarioData = message;
    console.log(formData.value);
    console.log('已填场景情绪:',formData.value);
    }

//最终提交Guide收集的表单formData
//其中包含触发最后一步对应的表单
const campaignForm = ref(null);
const store = useStore();
const campaignDataStage=ref('123');
const updateCampaignData = (message) => {
    console.log('Update Campaign');
    formData.value.campaignData = message;
    console.log(formData);
    console.log('已填营销目标:',formData.value);
    campaignDataStage.value = formData.value.campaignData.stage;
    console.log(campaignDataStage);
    next();
    };
const emit=defineEmits(['response','guideFormData']);
const showSpin=ref(false);
const submitGuideForm = async() =>{
    showSpin.value=true;
    const token = localStorage.getItem('token');
    const csrfToken= ref(getCsrfToken());
    senarioForm.value.createSenario();
    formData.value.type='new_copy';
    console.log('提交最终表单：',formData.value);
    emit('guideFormData',formData.value);
    try{
          const resp =  await axios.post('/api/test/',formData.value,{
            headers: {
                'Authorization': `Bearer ${token}`, // 设置请求头
                'X-CSRFToken': csrfToken.value,
                },
            withCredentials: true,});
          console.log(resp);
          emit('response',resp.data);
          emit('guideFormData',formData.value);
          store.commit('set_temp_campaign_data',formData.value.data);
         }catch (error) {
        console.error('Failed to get info:', error);
        }
    }

</script>
<style>

 .guide{
    margin:1.5em;
    margin-bottom:3em}

.n-card-header{
    font-size:1.5em;
    margin-left:1.2em;
    margin-top:0.8em
    }
.n-card{
    max-width:800px}
</style>
