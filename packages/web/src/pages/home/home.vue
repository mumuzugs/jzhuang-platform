<template>
  <view class="home-container">
    <!-- 顶部搜索区域 -->
    <view class="header">
      <view class="search-bar" @click="goToSearch">
        <Icon icon="mdi:magnify" :width="18" :height="18" color="#999" />
        <text class="search-placeholder">搜索装修方案、验房报告</text>
      </view>
    </view>
    
    <!-- Banner 轮播 -->
    <view class="banner-section">
      <swiper 
        class="banner-swiper" 
        :indicator-dots="true" 
        :autoplay="true" 
        :interval="3000"
        :circular="true"
        indicator-color="rgba(255,255,255,0.5)"
        indicator-active-color="#fff"
      >
        <swiper-item v-for="(item, index) in banners" :key="index">
          <image class="banner-image" :src="item.image" mode="aspectFill" @click="onBannerClick(item)" />
        </swiper-item>
      </swiper>
    </view>
    
    <!-- 快捷入口 -->
    <view class="quick-entry">
      <view 
        v-for="item in quickEntries" 
        :key="item.id" 
        class="entry-item"
        @click="onEntryClick(item)"
      >
        <view class="entry-icon" :style="{ background: item.bgColor }">
          <Icon :icon="item.icon" :width="28" :height="28" />
        </view>
        <text class="entry-name">{{ item.name }}</text>
      </view>
    </view>
    
    <!-- AI 验房卡片 -->
    <view class="module-card" @click="goToInspection">
      <view class="card-header">
        <view class="card-title">
          <Icon icon="mdi:home-search" :width="22" :height="22" color="#007AFF" />
          <text class="title-text">AI 智能验房</text>
        </view>
        <view class="card-tag">免费体验</view>
      </view>
      <view class="card-content">
        <view class="card-desc">
          <text>上传房间照片，AI 自动识别 8 类装修问题，生成专业验房报告</text>
        </view>
        <view class="card-features">
          <view class="feature-item" v-for="f in inspectionFeatures" :key="f">
            <Icon icon="mdi:check-circle" :width="14" :height="14" color="#52c41a" />
            <text>{{ f }}</text>
          </view>
        </view>
      </view>
      <view class="card-footer">
        <text class="start-btn">立即体验</text>
        <Icon icon="mdi:chevron-right" :width="18" :height="18" color="#007AFF" />
      </view>
    </view>
    
    <!-- AI 设计卡片 -->
    <view class="module-card" @click="goToDesign">
      <view class="card-header">
        <view class="card-title">
          <Icon icon="mdi:palette" :width="22" :height="22" color="#007AFF" />
          <text class="title-text">AI 设计预算联动</text>
        </view>
        <view class="card-tag">3套方案</view>
      </view>
      <view class="card-content">
        <view class="card-desc">
          <text>输入户型面积，AI 生成 3 套差异化设计方案，实时联动预算报价</text>
        </view>
        <view class="card-features">
          <view class="feature-item" v-for="f in designFeatures" :key="f">
            <Icon icon="mdi:check-circle" :width="14" :height="14" color="#52c41a" />
            <text>{{ f }}</text>
          </view>
        </view>
      </view>
      <view class="card-footer">
        <text class="start-btn">开始设计</text>
        <Icon icon="mdi:chevron-right" :width="18" :height="18" color="#007AFF" />
      </view>
    </view>
    
    <!-- 云监工卡片 -->
    <view class="module-card" @click="goToConstruction">
      <view class="card-header">
        <view class="card-title">
          <Icon icon="mdi:account-hard-hat" :width="22" :height="22" color="#007AFF" />
          <text class="title-text">云监工</text>
        </view>
        <view class="card-tag">实时跟踪</view>
      </view>
      <view class="card-content">
        <view class="card-desc">
          <text>标准化施工流程，8 大核心节点全程管控，延期主动预警</text>
        </view>
        <view class="card-features">
          <view class="feature-item" v-for="f in constructionFeatures" :key="f">
            <Icon icon="mdi:check-circle" :width="14" :height="14" color="#52c41a" />
            <text>{{ f }}</text>
          </view>
        </view>
      </view>
      <view class="card-footer">
        <text class="start-btn">查看我的施工</text>
        <Icon icon="mdi:chevron-right" :width="18" :height="18" color="#007AFF" />
      </view>
    </view>
    
    <!-- 底部 TabBar -->
    <TabBar />
    
    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import TabBar from '@/components/TabBar.vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// Banner 数据
const banners = ref([
  { id: 1, image: 'https://img.yzcdn.cn/vant/apple-1.jpg', url: '' },
  { id: 2, image: 'https://img.yzcdn.cn/vant/apple-2.jpg', url: '' },
])

// 快捷入口
const quickEntries = ref([
  { id: 1, name: 'AI验房', icon: 'mdi:home-search', bgColor: '#E8F4FF', path: '/pages/inspection/list/inspection-list' },
  { id: 2, name: '设计方案', icon: 'mdi:palette', bgColor: '#FFF3E8', path: '/pages/design/list/design-list' },
  { id: 3, name: '云监工', icon: 'mdi:account-hard-hat', bgColor: '#E8FFE8', path: '/pages/construction/list/construction-list' },
  { id: 4, name: '我的', icon: 'mdi:account', bgColor: '#FFE8F0', path: '/pages/mine/mine' },
])

// 功能特点
const inspectionFeatures = ['墙面开裂检测', '地面平整度分析', '防水渗漏识别', '水电隐患排查']
const designFeatures = ['现代简约风格', '新中式风格', '北欧风格', '实时预算联动']
const constructionFeatures = ['8大核心节点', '施工进度可视化', '延期预警提醒', '节点验收管理']

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
})

function goToSearch() {
  uni.showToast({ title: '搜索功能开发中', icon: 'none' })
}

function onBannerClick(item: any) {
  if (item.url) {
    uni.navigateTo({ url: item.url })
  }
}

function onEntryClick(item: any) {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/auth/login/login' })
    return
  }
  uni.switchTab({ url: item.path })
}

function goToInspection() {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/auth/login/login' })
    return
  }
  uni.switchTab({ url: '/pages/inspection/list/inspection-list' })
}

function goToDesign() {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/auth/login/login' })
    return
  }
  uni.switchTab({ url: '/pages/design/list/design-list' })
}

function goToConstruction() {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/auth/login/login' })
    return
  }
  uni.switchTab({ url: '/pages/construction/list/construction-list' })
}
</script>

<style lang="scss" scoped>
.home-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 180rpx;
}

.header {
  padding: 24rpx 32rpx;
  background: #fff;
  
  .search-bar {
    height: 72rpx;
    background: #f5f5f5;
    border-radius: 36rpx;
    display: flex;
    align-items: center;
    padding: 0 32rpx;
    gap: 12rpx;
    
    .search-placeholder {
      font-size: 28rpx;
      color: #999;
    }
  }
}

.banner-section {
  padding: 24rpx 32rpx;
  
  .banner-swiper {
    height: 300rpx;
    border-radius: 16rpx;
    overflow: hidden;
    
    .banner-image {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  }
}

.quick-entry {
  display: flex;
  justify-content: space-around;
  padding: 32rpx;
  background: #fff;
  margin: 0 32rpx;
  border-radius: 16rpx;
  
  .entry-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .entry-icon {
      width: 96rpx;
      height: 96rpx;
      border-radius: 24rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16rpx;
    }
    
    .entry-name {
      font-size: 26rpx;
      color: #333;
    }
  }
}

.module-card {
  margin: 32rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .card-title {
      display: flex;
      align-items: center;
      gap: 12rpx;
      
      .title-text {
        font-size: 34rpx;
        font-weight: 600;
        color: #333;
      }
    }
    
    .card-tag {
      font-size: 22rpx;
      color: #007AFF;
      background: #E8F4FF;
      padding: 8rpx 16rpx;
      border-radius: 8rpx;
    }
  }
  
  .card-content {
    .card-desc {
      font-size: 28rpx;
      color: #666;
      line-height: 1.6;
      margin-bottom: 24rpx;
    }
    
    .card-features {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16rpx;
      
      .feature-item {
        display: flex;
        align-items: center;
        gap: 8rpx;
        font-size: 24rpx;
        color: #666;
      }
    }
  }
  
  .card-footer {
    margin-top: 32rpx;
    padding-top: 24rpx;
    border-top: 1rpx solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .start-btn {
      font-size: 30rpx;
      color: #007AFF;
      font-weight: 500;
    }
  }
}

.bottom-placeholder {
  height: 120rpx;
}
</style>
