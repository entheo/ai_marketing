<!-- src/components/Login.vue -->
<template>
  <div>
    <h2>登录</h2>
    <form @submit.prevent="handleSubmit">
      <input type="text" v-model="username" placeholder="用户名" />
      <input type="password" v-model="password" placeholder="密码" />
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'LoginPage',
  setup() {
    const username = ref('');
    const password = ref('');
    const router = useRouter();

    const handleSubmit = () => {
      // 这里可以添加登录逻辑，例如调用API
      // 登录成功后，重定向到仪表板
      router.push('/dashboard');
    };

    return {
      username,
      password,
      handleSubmit,
    };
  },
};
</script>
