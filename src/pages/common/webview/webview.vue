<template>
  <view class="webview-container">
    <web-view :src="url" @load="onLoad" @error="onError"></web-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const url = ref('')

onMounted(() => {
  // 获取 URL 参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = (currentPage as any)?.options || {}
  
  if (options.url) {
    url.value = decodeURIComponent(options.url)
  } else {
    uni.showToast({ title: '无效的链接', icon: 'none' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  }
})

function onLoad() {
  uni.hideLoading()
}

function onError() {
  uni.showToast({ title: '页面加载失败', icon: 'none' })
}
</script>

<style lang="scss" scoped>
.webview-container {
  width: 100%;
  height: 100vh;
}
</style>
