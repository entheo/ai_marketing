<template>
  <n-notification-provider>
    <router-view> </router-view>
  </n-notification-provider>
</template>


<script>
import {NNotificationProvider} from 'naive-ui'
export default {
  name: 'App',
  components: {
      NNotificationProvider
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
