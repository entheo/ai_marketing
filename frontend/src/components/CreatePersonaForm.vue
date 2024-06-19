<!--CreatePersonaForm.vue-->
<template>
    <n-form label-placement="left" require-mark-placement="right-hanging" :label-width="labelWidth" size="large">
      <n-form-item label="他们是谁？">
        <n-input v-model:value='personaInfo.desc' clearable
          placeholder='例如：20岁左右刚刚大学毕业的年轻女生'/>
      </n-form-item>    
        <n-form-item label="主体性别:">
            <n-checkbox v-model:checked="personaInfo.male">
               男性
            </n-checkbox>
        <n-checkbox v-model:checked="personaInfo.female" :disabled="disabled">
               女性
        </n-checkbox>
    </n-form-item>

    <n-form-item label="相关的心理诉求是什么？">
        <n-input clearable v-model:value='personaInfo.motives' type="textarea" placeholder="例如：渴望快速建立自信，摆脱学生气，融入社会"/>
    </n-form-item>
    
    <n-form-item label="个人年收入范围?">
        <n-input v-model:value="personaInfo.salary" pair
          separator="-"
          :placeholder="placeholder"
          clearable
          @update:value="handleInputInput">
        </n-input>
    </n-form-item>
        
        <n-button v-show="false" @click="createPersona">保存</n-button>
    </n-form>
</template>

<script setup>
//import axios from 'axios';
import {onBeforeMount,ref,defineEmits,defineProps,defineExpose} from 'vue';
import { NButton, NForm,NFormItem, NInput, NCheckbox} from 'naive-ui';
import {useStore} from 'vuex';
//组件挂载前加载数据
const store = useStore();
onBeforeMount(()=>{
    preData.value = store.getters.temp_campaign_data;
    console.log('预加载数据：',preData.value);
    handlePersonaInfo();
    });
const preData = ref(null);
const handlePersonaInfo=()=>{
    console.log(typeof(preData.value));
    if(preData.value && JSON.stringify(preData.value)!=='{}' ){
       personaInfo.value.male = preData.value.personaData.male;
       personaInfo.value.female = preData.value.personaData.female;
       personaInfo.value.salary = preData.value.personaData.salary;
       personaInfo.value.motives = preData.value.personaData.motives;}
    };


//定义表单数据
const placeholder = ['人民币(万元)','人民币(万元)'];
const personaInfo = ref({
    male: false,
    female:false,
    salary:null,
    motives : '',
    })
const emit = defineEmits(['createdPersonaInfo']);
const createPersona = async() =>{
      emit('createdPersonaInfo',personaInfo.value);
      console.log('persona');
      console.log(personaInfo.value);
      /*try{
          
          const resp =  await axios.get('http://localhost:8005/account/auth/',{
            headers: {
                'Authorization': `Bearer ` // 设置请求头
                }});
          }catch (error) {
        console.error('Failed to fetch user info:', error);
        }*/
        
      }
const handleInputInput = () => {
    console.log('handle');
    }

defineExpose({createPersona,personaInfo});
defineProps({labelWidth:{default:190}});
</script>
<script>
  export default{
      name:'CreatePersonaForm'
      };
</script>

<style>
label{
    display:inline;
    width:auto;}
</style>
