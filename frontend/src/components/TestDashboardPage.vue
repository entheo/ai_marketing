<!--./testDashboard.vue-->

<template>

<n-layout position="absolute">
    <n-layout-header style="height: 64px; padding: 24px" bordered>
    步步为营
    </n-layout-header>

    <n-layout has-sider>
        <n-layout-sider
            bordered
            collapse-mode="width"
            :collapsed-width="64"
            :width="380"
            :collapsed="collapsed"
            show-trigger
            @collapse="collapsed = true"
            @expand="collapsed = false">
           
            <n-card>
            返回首页
            </n-card>
            
            <n-card>
            <n-flex justify="center">
              <n-button type='info'>编写全新文案</n-button>
              <n-button type='info'>优化已有文案</n-button>
            </n-flex>
            </n-card>
            <n-menu
                :collapsed="collapsed"
                :collapsed-width="64"
                :collapsed-icon-size="22"
                :options="menuOptions"/>

        </n-layout-sider>

        <n-layout-content>
            <n-split direction="horizontal" style="height:100%">
                <template #1>
                    <n-card :bordered="false" title="设置">
                    </n-card>
                </template>
                <template #2>
                    <n-card :bordered="false" title="内容" >
                    </n-card>
                </template>
            </n-split>
        </n-layout-content>
    
    </n-layout>
<n-layout-footer position="absolute"></n-layout-footer>
</n-layout>

</template>

<script setup>
import {NLayout,NLayoutHeader,NSplit,NLayoutContent,NLayoutSider,NMenu} from 'naive-ui';
import {NCard,NButton,NFlex} from 'naive-ui';

const menuOptions = [
  {
      label:"菜单一",
      key:"menu1",
      href:"/"
    },
  {
      label:"菜单2",
      key:"menu2",
      href:"/"
      }
];

</script>
<style>
.n-layout{
    height:100%}

</style>
