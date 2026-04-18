<template>
  <view class="tab-bar">
    <view 
      v-for="item in tabList" 
      :key="item.pagePath"
      class="tab-item"
      :class="{ active: currentPath === item.pagePath }"
      @click="switchTab(item)"
    >
      <view class="tab-icon">
        <Icon v-if="currentPath === item.pagePath" :icon="item.selectedIcon" :width="22" :height="22" />
        <Icon v-else :icon="item.icon" :width="22" :height="22" />
      </view>
      <text class="tab-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'

const tabList = [
  {
    pagePath: '/pages/home/home',
    text: '首页',
    icon: 'mdi:home-outline',
    selectedIcon: 'mdi:home',
  },
  {
    pagePath: '/pages/inspection/list/inspection-list',
    text: '验房',
    icon: 'mdi:magnify',
    selectedIcon: 'mdi:magnify',
  },
  {
    pagePath: '/pages/design/list/design-list',
    text: '设计',
    icon: 'mdi:palette-outline',
    selectedIcon: 'mdi:palette',
  },
  {
    pagePath: '/pages/construction/list/construction-list',
    text: '施工',
    icon: 'mdi:account-hard-hat-outline',
    selectedIcon: 'mdi:account-hard-hat',
  },
  {
    pagePath: '/pages/mine/mine',
    text: '我的',
    icon: 'mdi:account-outline',
    selectedIcon: 'mdi:account',
  },
]

const currentPath = ref('/pages/home/home')

onMounted(() => {
  // 获取当前页面路径
  const pages = getCurrentPages()
  if (pages.length > 0) {
    const currentPage = pages[pages.length - 1]
    currentPath.value = '/' + currentPage.route
  }
})

function switchTab(item: any) {
  if (currentPath.value === item.pagePath) return
  
  uni.switchTab({
    url: item.pagePath
  })
}
</script>

<style lang="scss" scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  padding-bottom: env(safe-area-inset-bottom);
  background: #fff;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
  z-index: 999;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rpx 0;
  color: #999;
  
  &.active {
    color: #007AFF;
  }
  
  .tab-icon {
    margin-bottom: 4rpx;
  }
  
  .tab-text {
    font-size: 22rpx;
  }
}
</style>
