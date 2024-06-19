<template>
<div class="quote-container" v-if="currentQuote">
    <!--
    <div class="quote" v-show="visible">{{ currentQuote.quote }}</div>
    <div class="author" v-show="visible">— {{ currentQuote.author }}</div>
    -->
    <div class="quote" :class="{ 'visible': visible }">{{ currentQuote.quote }}</div>
     <p style="line-height: 0.5">&nbsp;</p>
    <div class="author" :class="{ 'visible': visible }">— {{ currentQuote.author }}</div>
  
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import quotes from './quotes.js';

const currentQuote = ref(quotes[0]);
//const currentQuote = ref(null);
const visible = ref(false);
let index = 0;

function showNextQuote() {
  visible.value = false;
  /*
  currentQuote.value = quotes[index % quotes.length];
  index++;
  setTimeout(() => {
    visible.value = false;
  }, 18000); // 4秒后开始隐藏名言，给出总共6秒的间隔
 */
 setTimeout(() => {
    index = (index + 1) % quotes.length;
    currentQuote.value = quotes[index];
    visible.value = true;
  }, 18000); // 1秒后显示下一条名言，允许完全隐藏
}

onMounted(() => {
  const interval = setInterval(showNextQuote, 20000); // 每6秒更换名言
  showNextQuote();

  onUnmounted(() => {
    clearInterval(interval);
  });
});
</script>

<style>
.quote-container {
  transition: opacity 2s;
}

.quote, .author {
  opacity: 0;
  transition: opacity 2s;
}

.quote-container .quote, .quote-container .author {
  opacity: 1;
}
</style>
