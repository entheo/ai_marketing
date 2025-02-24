<template>
  <n-form label-placement="left" require-mark-placement="right-hanging" label-width="180" size="large">
    
    <n-form-item label="名称:">
      <n-input 
        v-model:value="accountName"
        maxlength="24"
        show-count
        type="text"
        size="large"
        clearable
      />
     </n-form-item>
    
     <n-form-item label="简介">
      <n-input
        v-model:value="accountIntro"
        maxlength="200"
        show-count
        type="textarea"
        :autosize="{minRows:4,maxRow:4}"
        clearable
      />
    </n-form-item>
  
  <n-button v-show="false" @click="updateRednoteInfo" type="info" size="large">确定
  </n-button>

  </n-form>
</template>

<script setup>
import {NForm, NFormItem, NInput, NButton} from 'naive-ui';
import {ref,defineEmits,defineExpose} from 'vue';

const accountName = ref(null);
const accountIntro = ref(null);
const infoType = 'rednote'

const emit = defineEmits(['accountName','accountIntro'])
const updateRednoteInfo = () => {
    emit ('accountInfo',{name:accountName.value,intro:accountIntro.value,type:infoType});
    }

defineExpose({updateRednoteInfo});
</script>
