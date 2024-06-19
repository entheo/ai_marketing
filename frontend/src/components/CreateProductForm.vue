<template>
  <n-form label-placement="left" require-mark-placement="right-hanging" label-width="180" size="large">
    <n-form-item label="所属品牌名称:">
        <n-input clearable v-model:value="productInfo.brandName" placeholder=""/>
    </n-form-item>

    <n-form-item label="品牌提倡理念:">
        <n-input v-model:value="productInfo.brandValues" clearable type="textarea" placeholder=""/>
    </n-form-item>
    
    <n-form-item label="产品或服务的名称:">
        <n-input clearable v-model:value="productInfo.name" placeholder=""/>
    </n-form-item>

    <n-form-item label="独特卖点(USP):">
         <n-input v-model:value="productInfo.usp" clearable type="textarea" placeholder=""/>
    </n-form-item>
    
    <n-button v-show="false" @click="createProduct">保存</n-button>
</n-form>
</template>

<script setup>
import {ref,defineEmits,defineExpose} from 'vue';
import {NButton, NForm, NFormItem,NInput} from 'naive-ui';
const productInfo = ref({
    brandName : '',
    brandValues:'',
    name : '',
    usp : '',
    })
const emit = defineEmits(['createdProductInfo']);
const createProduct = () =>{
      emit('createdProductInfo',productInfo.value);
      console.log(productInfo.value);
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
defineExpose({createProduct});
</script>
<script>
  export default{
      name:'CreateProductForm'
      };
</script>
