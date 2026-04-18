<template>
  <view class="index-container">
    <text class="title">集装修</text>
    <text class="subtitle">一站式装修服务平台</text>
  </view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  // 检查登录状态
  const token = uni.getStorageSync('jzhuang_token')
  if (token) {
    // 已登录，跳转到首页
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/home' })
    }, 1500)
  } else {
    // 未登录，跳转到登录页
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/auth/login/login' })
    }, 1500)
  }
})
</script>

<style lang="scss" scoped>
.index-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #f0f5ff 0%, #ffffff 100%);
  
  .title {
    font-size: 64rpx;
    font-weight: 700;
    color: #007AFF;
    margin-bottom: 16rpx;
  }
  
  .subtitle {
    font-size: 28rpx;
    color: #999;
  }
}
</style>
