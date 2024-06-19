<template>
    <n-button @click="copyText">复制</n-button>
</template>

<script setup>
import {useNotification} from 'naive-ui'
const notification = useNotification();

const copyText = () => {
  // 这里是点击按钮后要执行的操作。
  // 作为示例，我们直接触发通知。
  // 实际使用时，你可以将这里替换为其他逻辑，比如复制文本到剪贴板等。
  notification.success({
    content: '复制成功',
    duration: 2000,
  });
};
</script>
