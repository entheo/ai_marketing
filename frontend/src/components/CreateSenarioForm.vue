<template>
    <n-form :label-placement="labelPlacement" require-mark-placement="right-hanging" :label-width="labelWidth" size="large">

        <div class="tricks" v-show='has_stage'>
            <n-card embeded :bordered="false">
              <span class='senario'>目前所处【{{campaignStage}}】，较适合场景：{{senario}}</span>
            </n-card>
          </div>
        <n-form-item label="计划将文案用在哪里？" size="large">
            <n-radio-group 
                class="radio-group-wrap"
                style="--n-button-border-color:none;--n-button-border-color-active: none;--n-height:auto"
                v-model:value="senarioInfo.places" 
                size="large"
                name="radiobuttongroup1"
                @update:value="getPlace">
        
                <n-radio-button class="bordered-button"
                    v-for="place in places"
                    :key="place.value"
                    :value="place.value"
                    :label="place.label"/> 
            </n-radio-group>
        </n-form-item>
        
        <n-form-item label="补充描述使用场景:" v-show="otherPlace">              <n-input 
                v-show="otherPlace" 
                v-model:value='otherPlaceData' placeholder=""
                clearable
                ref="inputInstRef"/>
        </n-form-item>
        
        <div class="tricks" v-show="has_senario">
          <n-card  embedded :bordered="false" >
            <n-icon><bulb-outline/></n-icon>
            <span>场景特点提示</span>
            <div v-html="markdownTricks"></div>
         </n-card>
        </div>

        <n-form-item class="tags" label="传递情绪与感受是？">
         <n-dynamic-tags v-model:value="senarioInfo.emotionTags" :render-tag="renderEmotionTags" />
         </n-form-item>
         
        <n-button v-show="false" type="primary" @click="createSenario">保存</n-button>
    </n-form>
</template>

<script setup>
import {watchEffect,computed,onBeforeMount,ref,h, defineEmits,defineExpose,defineProps} from 'vue';
import {NIcon,NCard,NRadioGroup,NRadioButton,NButton, NForm, NInput, NFormItem,  NTag,NDynamicTags} from 'naive-ui';
import {useStore} from 'vuex';
import {BulbOutline} from '@vicons/ionicons5';
import MarkdownIt from 'markdown-it';

//组件挂载前加载数据
const store = useStore();
onBeforeMount(()=>{
    preData.value = store.getters.temp_campaign_data;
    console.log('预加载数据：',preData.value);
    handleSenarioInfo();
    });
const preData = ref(null);
const handleSenarioInfo=()=>{
    console.log(typeof(preData.value));
    if(preData.value && JSON.stringify(preData.value)!=='{}' ){
       senarioInfo.value.places = preData.value.senarioData.places;
       senarioInfo.value.emotionTags = preData.value.senarioData.emotionTags;
    }};

//定义表单
const inputInstRef=ref(null);
const otherPlace=ref(false);
const otherPlaceData=ref(null);
const places = [
    {
        value:"微信朋友圈",
        label:"微信朋友圈",
        },
    {
        value:"微信群内",
        label:"微信群内",
        },
    {
        value:"小红书",
        label:"小红书",
        },
    {
        value:"电商/商品详情页",
        label:"电商/商品详情页",
        },

    {
        value:"其它...",
        label:"其它",
        },
];
const has_senario = ref(false);
const senarioTrick=ref('');
const getPlace = (message)=>{
    has_senario.value=true;
    otherPlace.value=false;
    switch(message){
        case '微信朋友圈':
        senarioInfo.value.emotionTags=['真实','真诚','亲密感'];
        senarioTrick.value= '**微信朋友圈是私人社交场所——**  \n 人们期待在这里看到彼此"真实"与"真诚"的一面，通常会对广告等商业属性强烈的信息感到不适。';
        break

        case '微信群内':
        senarioInfo.value.emotionTags=['价值感','行动感','归属感'];
        senarioTrick.value='**微信群是一个价值互动场所——**  \n  相对于朋友圈，人们对于这里的价值感预期更高。不管是情感、知识、新闻、还是优惠，都要确保对群成员有用，要避免过多相关性较低内容导致人们的期待落空。';
        break;

        case '小红书':
        senarioInfo.value.emotionTags=['探索欲','真实感','认同感'];
        senarioTrick.value='**小红书是一个分享兴趣与生活方式灵感的地方——**  \n  人们希望在这里看到不同生活方式的精彩之处的同时与兴趣好友建立联系，获得超越现有熟人关系以外的认同感。';
        break;

        case '电商/商品详情页':
        senarioTrick.value='**商品详情页面进行付费决策的地方——**  \n  在这里所有信息都应该用来推动消费者快速形成下单，比如打消疑惑、加强信任、释放优惠等。';
        senarioInfo.value.emotionTags=['信任','诱惑','紧迫感']
        
        break;
        
        case '其它...':
        senarioInfo.value.places='';
        senarioInfo.value.emotionTags=['惊喜'];
        otherPlace.value=true;
        inputInstRef.value?.focus();
        has_senario.value=false;
        }
    };

const md= MarkdownIt()
const markdownTricks=computed(()=>{
    console.log(senarioTrick.value);
    return md.render(senarioTrick.value)});
const emotionTagsRef = ref(["喜悦", "真诚"]);
const senarioInfo = ref({
    places:'',
    emotionTags: emotionTagsRef,

    })
const renderEmotionTags = (tag, index) => {
      return h(
          NTag,
          {
            type: index < 3 ? "success" : "error",
            disabled: index > 3,
            closable: true,
            onClose: () => {
              emotionTagsRef.value.splice(index, 1);
            }
          },
           ()=> tag
        )
}
const emit = defineEmits(['senarioInfoCreated']);
const createSenario = () =>{
    console.log('to create senario');
    console.log(senarioInfo.value);
    if(otherPlaceData.value && JSON.stringify(otherPlaceData.value)!==''){
          senarioInfo.value.places=otherPlaceData.value}
      emit('senarioInfoCreated',senarioInfo.value);
      try{
          /*
          const resp =  await axios.get('http://localhost:8005/account/auth/',{
            headers: {
                'Authorization': `Bearer ${token}` // 设置请求头
                }});
         */ }catch (error) {
        console.error('Failed to fetch user info:', error);
        }
      };

defineExpose({createSenario,senarioInfo,otherPlaceData,otherPlace,places});
const props = defineProps({
    labelWidth:{default:'190'},
    labelPlacement:{default:'left'},
    campaignStage:{},
    });
const has_stage=ref(false);
watchEffect(()=>{
    getSenarioTrick(props.campaignStage);
    });
//根据stage来返回推荐场景
const senario = ref('');
function getSenarioTrick(stage){
    console.log(stage);
    if(stage==null){
        has_stage.value=false}
    switch(stage){
        case '意识阶段':
          senario.value='微信朋友圈';
          has_stage.value=true;
          break;
        case '兴趣阶段':
          senario.value='微信朋友圈、小红书';
          has_stage.value=true;
          break;
        case '考虑阶段':
          senario.value='微信群内、小红书';
          has_stage.value=true;
          break;
        case '意向阶段':
          senario.value='微信群内';
          has_stage.value=true;
          break;
        case '行动阶段':
          senario.value='微信群内、商品详情页';
          has_stage.value=true;
          break;
        case '忠诚度建立阶段':
          senario.value='微信群内、小红书';
          has_stage.value=true;
          break;
        case '推荐阶段':
          senario.value='微信朋友圈、小红书';
          has_stage.value=true;
          break;
    }}
</script>

<script>
  export default{
      name:'CreateSenarioForm'
      };
</script>

<style scoped>
.n-space{
    margin:0}
.tags .n-form-item-blank .n-space{
    margin:0;
    }
.radio-group-wrap {
  display: flex;
  flex-wrap: wrap; 
}
.radio-group-wrap .bordered-button{
    border:1px solid;
    border-color:rgb(224, 224, 230);
    margin-right:10px;
    margin-bottom:10px;
    height:38px;
    line-height:2.5}

.n-card__content {
    padding:0px 14px 0px 0px}
.tricks {
    text-align:left;
    marigin-bottom:20px;}
.tricks .senario{
    background:#f9f9cf}
.tricks .n-card__content{
    padding-bottom:0;}
</style>
