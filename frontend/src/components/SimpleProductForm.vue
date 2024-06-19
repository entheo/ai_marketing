<!--SimpleProductForm.vue-->>
<template>
    <n-form label-placement="left" require-mark-placement="right-hanging" :label-width="labelWidth" size="large">
    
    <n-form-item label="产品或服务叫什么？">
        <n-input clearable v-model:value="productInfo.name" placeholder="如果暂无正式名称，可以先用使用品类替代"/>
    </n-form-item>

    <n-form-item label="独特卖点是什么？">
         <n-input v-model:value="productInfo.usp" clearable type="textarea" placeholder="它是什么？有什么与众不同的特点或者优势？"/>
    </n-form-item>

    <n-form-item label="是否有提倡的品牌理念？">
        <n-input v-model:value="productInfo.brandValues" clearable type="textarea" placeholder="如果有的话，有助于加强与客户的情感连接"/>
    </n-form-item>
    
    <n-button v-show="false" @click="createProduct">保存</n-button>
</n-form>
</template>

<script setup>
import {onBeforeMount,ref,defineEmits,defineExpose,defineProps} from 'vue';
import {NButton, NForm, NFormItem,NInput} from 'naive-ui';
import {useStore} from 'vuex';
//组件挂载前加载数据
const store = useStore();
onBeforeMount(()=>{
    preData.value = store.getters.temp_campaign_data;
    console.log('预加载数据：',preData.value);
    handleProductInfo();
    });
const preData = ref(null);
const handleProductInfo=()=>{
    console.log(typeof(preData.value));
    if(preData.value && JSON.stringify(preData.value)!=='{}' ){
       productInfo.value.name = preData.value.productData.name;
       productInfo.value.usp = preData.value.productData.usp;
       productInfo.value.brandValues = preData.value.productData.brandValues;}
    };

//定义表单变量
const productInfo = ref({
    name:'',
    usp:'',
    brandValues:'',
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
defineExpose({createProduct,productInfo});
defineProps({labelWidth:{default:190}});
</script>
<script>
  export default{
      name:'SimpleProductForm'
      };
</script>
