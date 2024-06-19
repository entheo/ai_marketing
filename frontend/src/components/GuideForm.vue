<!--GuideForm-->

<template>
  <n-space vertical>
    <n-steps :current="Number(current)" :status="currentStatus">
      <n-step
        title="营销目标"
        description="设定清晰的营销目标是成功的第一步,要尽力确保营销工作的重要环节都能做到有的放矢"
      >
      
      </n-step>
      <n-step
        title="客户画像"
        description="勾勒目标客户画像可以更精准地定位市场，并制定出能够引起目标客户共鸣的营销信息"
      />
      <n-step
        title="产品描述"
        description="好的产品描述能够激发潜在客户的购买欲望，并建立产品与客户之间的情感联系"
      />
      <n-step
        title="场景&情绪"
        description="营造恰当的场景情绪可以极大地影响客户的感知和行为，促使目标客户采取行动"
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

<n-card :bordered="false" v-show="currentRef==1">
  <create-campaign-form @createdCampaignInfo="updateCampaignData" ref="campaignForm"/>
  
  <n-flex justify="center">
    <n-button type="info" @click="saveCampaignForm">保存并下一步</n-button>
  </n-flex>

</n-card>

<n-card :bordered="false" v-show="currentRef==2">
<create-persona-form @createdPersonaInfo = "updatePersonaData" ref="personaForm"/>
<n-flex justify="center">
<n-button @click="prev">上一步</n-button>
<n-button type="info" @click="savePersonaForm">保存并下一步</n-button>
</n-flex>
</n-card>

<n-card :bordered="false" v-show="currentRef==3">
<create-product-form @createdProductInfo = "updateProductData" ref="productForm"/>
<n-flex justify="center">
<n-button @click="prev">上一步</n-button>
<n-button type="info" @click="saveProductForm">保存并下一步</n-button>
</n-flex>
</n-card>

<n-card :bordered="false" v-show="currentRef==4">
<create-senario-form @senarioInfoCreated="updateSenarioData" ref="senarioForm"/>
<n-flex justfiy="center">
<n-button @click="prev">上一步</n-button>
<n-button type="primary" @click="submitGuideForm">保存并提交</n-button>
</n-flex>
</n-card>


</template>

<script setup>
import {ref,defineProps,watch} from 'vue';
import axios from 'axios';
//import { MdArrowRoundBack, MdArrowRoundForward } from '@vicons/ionicons4';
import { NFlex, NCard,  NStep, NSpace, NButton,NSteps} from 'naive-ui';
import CreateCampaignForm from './CreateCampaignForm.vue';
import CreatePersonaForm from './CreatePersonaForm.vue';
import CreateProductForm from './CreateProductForm.vue';
import CreateSenarioForm from './CreateSenarioForm.vue';


const getCsrfToken = () => {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken'))
    ?.split('=')[1];
};

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

const campaignForm = ref(null);
const saveCampaignForm = () =>{
    campaignForm.value.createCampaign();   
    }
const updateCampaignData = (message) => {
    console.log('Update Campaign');
    formData.value.campaignData = message;
    console.log(formData);
    next();
    };

const personaForm = ref(null);
const savePersonaForm = () => {
    personaForm.value.createPersona();
    }
const updatePersonaData = (message) => {
    console.log('Update Persona');
    formData.value.personaData = message;
    console.log(formData);
    next();
    };

const productForm = ref(null);
const saveProductForm = () => {
    productForm.value.createProduct();
    }
const updateProductData = (message) => {
    console.log('Update Product');
    formData.value.productData = message;
    console.log(formData);
    next();
    };

const senarioForm = ref(null);
const submitGuideForm = async() =>{
    const token = localStorage.getItem('token');
    const csrfToken= ref(getCsrfToken());
    senarioForm.value.createSenario();
    console.log('最终表单');
    console.log(formData);
    try{
          const resp =  await axios.post('/api/assistant/',formData,{
            headers: {
                'Authorization': `Bearer ${token}`, // 设置请求头
                'X-CSRFToken': csrfToken.value,
                },
            withCredentials: true,});
          console.log(resp);
         }catch (error) {
        console.error('Failed to get info:', error);
        }
    }
const updateSenarioData = (message) => {
    console.log('Update Senario');
    formData.value.senarioData = message;
    console.log(formData);
    }

</script>
<style>
.n-space{
    margin:1.5em;}
.n-card-header{
    font-size:1.5em;
    margin-left:1.2em;
    margin-top:0.8em
    }
.n-card{
    max-width:800px}
</style>
