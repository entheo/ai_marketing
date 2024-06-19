
<template>
   
    <div>
        <form @submit.prevent="submitForm">
          <label>
            上下文：
            <input v-model="formData.context" type="text">
          </label>
          <label>
            写作目标：
            <input v-model="formData.goal" type="text">
          </label>

          <label>
            行文风格：
            <input v-model="formData.style" type="text">
          </label>

          <label>
            情绪语气：
            <input v-model="formData.tone" type="text">
          </label>

          <label>
            受众画像：
            <input v-model="formData.audience" type="text">
          </label>
          
          <label>
            输出要求：
            <input v-model="formData.output" type="text">
          </label>
          <!-- 增加其他表单字段 -->
          <button type="submit">提交</button>
        </form>
    </div>

  <div>{{ message }}</div>
  <button @click="handleClick">点击</button>

</template>

<script>
import axios from 'axios'; // 引入axios库

export default {
  data() {
    return {
      message: '', // 定义message变量，用于存储api返回的数据
      formData:{
          context:'',
          goal:'',
          style:'',
          tone:'',
          audience:'',
          output:''
          }
    }
  },
  components:{
      },

  methods: {
     handleClick() {
       axios.get('http://localhost:8002/api/response/?format=json')  //你的Django后端API的endpoint
          .then(response => {
             //在这里处理你的数据。response.data将包含你的数据。
             console.log(response.data);
             this.message = response.data.message;
          })
          .catch(error => {
             //在这里处理错误
             console.error(error);
          }); 
        },

    submitForm() {
      axios.post('http://localhost:8002/api/response/', this.formData)
          .then(response => {
            // 处理你后端返回的response
            console.log(response);
            this.message = response.data.message;
        })
        .catch(err => {
          console.log(err);
        });
    }
   },

  mounted() {
  }
}
</script>
