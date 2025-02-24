<template>
  <n-form>
        <n-form-item>
          <n-input v-model:value="copyOriginal" maxlength="2000" show-count type="textarea" placeholder="请将原文内容复制粘贴到这里...（2000字以内）" :autosize="{minRows:4,maxRows:4}" clearable/>
        </n-form-item>
    <n-button v-show="false" @click="updateCopyOriginal" type="info" size="large">确定</n-button>
  </n-form>
</template>

<script setup>
import {NForm, NFormItem, NInput, NButton} from 'naive-ui';
import {ref,defineEmits,defineExpose} from 'vue';

const copyOriginal = ref(null);
const infoType = 'article'
const emit = defineEmits(['copyOriginalInfo'])
const updateCopyOriginal = ()=>{
    emit('copyOriginalInfo',{info:copyOriginal.value,type:infoType});
    }

defineExpose({updateCopyOriginal});
</script>
