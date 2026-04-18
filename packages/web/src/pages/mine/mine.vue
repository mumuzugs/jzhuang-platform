<template>
  <view class="mine-container">
    <!-- 用户信息区域 -->
    <view class="user-section">
      <view class="user-info" v-if="userStore.isLoggedIn" @click="goToProfile">
        <image class="avatar" :src="userStore.userInfo?.avatar || '/static/default-avatar.png'" />
        <view class="info-text">
          <text class="nickname">{{ userStore.userInfo?.nickname || userStore.phone }}</text>
          <view class="vip-badge" v-if="userStore.isVip">
            <text class="vip-icon">⭐</text>
            <text class="vip-text">VIP会员</text>
          </view>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="login-prompt" v-else @click="goToLogin">
        <image class="avatar" src="/static/default-avatar.png" />
        <text class="login-text">点击登录</text>
        <text class="arrow">›</text>
      </view>
    </view>
    
    <!-- 会员卡片 -->
    <view class="vip-card" @click="goToVip" v-if="userStore.isLoggedIn">
      <view class="vip-content">
        <view class="vip-title">
          <text class="vip-icon">💎</text>
          <text class="vip-name">{{ userStore.isVip ? 'VIP会员' : '开通VIP' }}</text>
        </view>
        <text class="vip-desc" v-if="!userStore.isVip">解锁更多功能，尊享专属服务</text>
        <text class="vip-desc" v-else>尊享全部功能特权</text>
      </view>
      <view class="vip-action">
        <text v-if="userStore.isVip">已开通</text>
        <text v-else>立即开通</text>
      </view>
    </view>
    
    <!-- 功能列表 -->
    <view class="menu-section">
      <view class="menu-item" @click="goToPage('/pages/mine/orders/orders')">
        <text class="menu-icon">📋</text>
        <text class="menu-text">我的订单</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goToPage('/pages/mine/favorites/favorites')">
        <text class="menu-icon">❤️</text>
        <text class="menu-text">我的收藏</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goToPage('/pages/mine/history/history')">
        <text class="menu-icon">🕐</text>
        <text class="menu-text">浏览历史</text>
        <text class="arrow">›</text>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="menu-item" @click="goToPage('/pages/mine/settings/settings')">
        <text class="menu-icon">⚙️</text>
        <text class="menu-text">设置</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goToPage('/pages/mine/help/help')">
        <text class="menu-icon">❓</text>
        <text class="menu-text">帮助与反馈</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goToPage('/pages/mine/about/about')">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于我们</text>
        <text class="arrow">›</text>
      </view>
    </view>
    
    <!-- 退出登录 -->
    <view class="logout-section" v-if="userStore.isLoggedIn">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>
    
    <!-- 底部 TabBar -->
    <TabBar />
    
    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import TabBar from '@/components/TabBar.vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
})

function goToLogin() {
  uni.navigateTo({ url: '/pages/auth/login/login' })
}

function goToProfile() {
  uni.navigateTo({ url: '/pages/mine/profile/profile' })
}

function goToVip() {
  if (!userStore.isLoggedIn) {
    goToLogin()
    return
  }
  if (!userStore.isVip) {
    uni.navigateTo({ url: '/pages/mine/vip/vip' })
  }
}

function goToPage(url: string) {
  if (!userStore.isLoggedIn) {
    goToLogin()
    return
  }
  uni.navigateTo({ url })
}

async function handleLogout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: async (res) => {
      if (res.confirm) {
        await userStore.logout()
        uni.showToast({ title: '已退出登录', icon: 'success' })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.mine-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 180rpx;
}

.user-section {
  background: linear-gradient(135deg, #007AFF 0%, #0056FF 100%);
  padding: 60rpx 32rpx 80rpx;
  
  .user-info,
  .login-prompt {
    display: flex;
    align-items: center;
    
    .avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 60rpx;
      background: #fff;
      margin-right: 24rpx;
    }
    
    .info-text {
      flex: 1;
      
      .nickname {
        font-size: 36rpx;
        font-weight: 600;
        color: #fff;
        display: block;
        margin-bottom: 12rpx;
      }
      
      .vip-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 215, 0, 0.2);
        padding: 6rpx 16rpx;
        border-radius: 20rpx;
        
        .vip-icon {
          font-size: 24rpx;
          margin-right: 8rpx;
        }
        
        .vip-text {
          font-size: 22rpx;
          color: #FFD700;
        }
      }
    }
    
    .login-text {
      flex: 1;
      font-size: 36rpx;
      color: #fff;
      font-weight: 500;
    }
    
    .arrow {
      font-size: 40rpx;
      color: rgba(255, 255, 255, 0.6);
    }
  }
}

.vip-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  margin: -40rpx 32rpx 24rpx;
  padding: 28rpx 32rpx;
  border-radius: 16rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  
  .vip-content {
    .vip-title {
      display: flex;
      align-items: center;
      margin-bottom: 8rpx;
      
      .vip-icon {
        font-size: 32rpx;
        margin-right: 12rpx;
      }
      
      .vip-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #FFD700;
      }
    }
    
    .vip-desc {
      font-size: 24rpx;
      color: rgba(255, 255, 255, 0.6);
    }
  }
  
  .vip-action {
    font-size: 26rpx;
    color: #FFD700;
  }
}

.menu-section {
  background: #fff;
  margin-bottom: 24rpx;
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 32rpx;
    border-bottom: 1rpx solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .menu-icon {
      font-size: 40rpx;
      margin-right: 24rpx;
    }
    
    .menu-text {
      flex: 1;
      font-size: 30rpx;
      color: #333;
    }
    
    .arrow {
      font-size: 32rpx;
      color: #ccc;
    }
  }
}

.logout-section {
  padding: 48rpx 32rpx;
  
  .logout-btn {
    width: 100%;
    height: 88rpx;
    background: #fff;
    color: #ff4d4f;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: none;
  }
}

.bottom-placeholder {
  height: 120rpx;
}
</style>
