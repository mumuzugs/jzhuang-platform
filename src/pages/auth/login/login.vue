<template>
  <view class="login-container">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
    </view>
    
    <!-- Logo 区域 -->
    <view class="logo-section">
      <view class="logo-wrapper">
        <Icon icon="mdi:home-city" :width="80" :height="80" color="#007AFF" />
      </view>
      <text class="app-name">集装修</text>
      <text class="app-slogan">一站式装修服务平台</text>
    </view>
    
    <!-- 登录表单 -->
    <view class="form-section">
      <view class="input-group">
        <view class="input-item">
          <text class="input-label">手机号</text>
          <input 
            v-model="form.phone" 
            type="number" 
            maxlength="11" 
            placeholder="请输入手机号"
            class="input"
          />
        </view>
        
        <view class="input-item">
          <text class="input-label">验证码</text>
          <view class="code-input-wrapper">
            <input 
              v-model="form.code" 
              type="number" 
              maxlength="6" 
              placeholder="请输入验证码"
              class="input code-input"
            />
            <button 
              class="code-btn" 
              :disabled="countdown > 0"
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </button>
          </view>
        </view>
      </view>
      
      <!-- 登录按钮 -->
      <button class="login-btn" :loading="loading" @click="handleLogin">
        登录
      </button>
      
      <!-- 其他登录方式 -->
      <view class="other-login">
        <text class="other-login-text">其他登录方式</text>
        <view class="other-login-icons">
          <view class="wechat-btn" @click="wechatLogin">
            <Icon icon="mdi:wechat" :width="40" :height="40" color="#07C160" />
          </view>
        </view>
      </view>
      
      <!-- 用户协议 -->
      <view class="agreement">
        <checkbox-group @change="onAgreementChange">
          <label>
            <checkbox :checked="agreed" color="#007AFF" style="transform: scale(0.8)" />
            <text class="agreement-text">我已阅读并同意</text>
            <text class="link" @click="goToAgreement('user')">《用户协议》</text>
            <text class="agreement-text">和</text>
            <text class="link" @click="goToAgreement('privacy')">《隐私政策》</text>
          </label>
        </checkbox-group>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Icon } from '@iconify/vue'
import { sendCode as apiSendCode, loginByCode } from '@/api/auth'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const form = reactive({
  phone: '',
  code: '',
})

const loading = ref(false)
const countdown = ref(0)
const agreed = ref(false)

async function sendCode() {
  if (!form.phone || form.phone.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  try {
    await apiSendCode(form.phone)
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (e: any) {
    uni.showToast({ title: e.message || '发送失败', icon: 'none' })
  }
}

async function handleLogin() {
  if (!agreed.value) {
    uni.showToast({ title: '请先阅读并同意用户协议', icon: 'none' })
    return
  }
  
  if (!form.phone || form.phone.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  if (!form.code || form.code.length !== 6) {
    uni.showToast({ title: '请输入6位验证码', icon: 'none' })
    return
  }
  
  loading.value = true
  try {
    const res = await loginByCode({
      phone: form.phone,
      code: form.code,
    })
    
    userStore.loginSuccess(res.access_token, res.user)
    uni.showToast({ title: '登录成功', icon: 'success' })
    
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/home' })
    }, 1000)
  } catch (e: any) {
    uni.showToast({ title: e.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function wechatLogin() {
  // #ifdef MP-WEIXIN
  wx.getPhoneNumber({
    success: async (res) => {
      console.log('微信手机号', res)
    },
    fail: (err) => {
      console.error('微信登录失败', err)
    }
  })
  // #endif
  
  // #ifndef MP-WEIXIN
  uni.showToast({ title: '请在微信小程序中使用', icon: 'none' })
  // #endif
}

function onAgreementChange(e: any) {
  agreed.value = e.detail.value.length > 0
}

function goToAgreement(type: 'user' | 'privacy') {
  uni.navigateTo({
    url: `/pages/common/webview/webview?url=https://jizhuang.cn/${type}.html`
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f5ff 0%, #ffffff 100%);
  padding: 0 40rpx;
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  
  .circle {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(0, 122, 255, 0.1) 0%, rgba(0, 122, 255, 0.05) 100%);
  }
  
  .circle-1 {
    width: 400rpx;
    height: 400rpx;
    top: -100rpx;
    right: -100rpx;
  }
  
  .circle-2 {
    width: 300rpx;
    height: 300rpx;
    top: 400rpx;
    left: -150rpx;
  }
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 160rpx;
  
  .logo-wrapper {
    width: 160rpx;
    height: 160rpx;
    background: #fff;
    border-radius: 40rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24rpx;
    box-shadow: 0 8rpx 32rpx rgba(0, 122, 255, 0.15);
  }
  
  .app-name {
    font-size: 48rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
  }
  
  .app-slogan {
    font-size: 28rpx;
    color: #999;
  }
}

.form-section {
  margin-top: 80rpx;
  
  .input-group {
    background: #fff;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
    
    .input-item {
      margin-bottom: 32rpx;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .input-label {
      display: block;
      font-size: 28rpx;
      color: #666;
      margin-bottom: 16rpx;
    }
    
    .input {
      height: 88rpx;
      background: #f8f8f8;
      border-radius: 16rpx;
      padding: 0 24rpx;
      font-size: 32rpx;
    }
    
    .code-input-wrapper {
      display: flex;
      align-items: center;
      gap: 24rpx;
      
      .code-input {
        flex: 1;
      }
      
      .code-btn {
        width: 220rpx;
        height: 88rpx;
        background: linear-gradient(135deg, #007AFF 0%, #0056FF 100%);
        color: #fff;
        font-size: 26rpx;
        border-radius: 16rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        border: none;
        
        &[disabled] {
          background: #ccc;
        }
      }
    }
  }
  
  .login-btn {
    width: 100%;
    height: 96rpx;
    background: linear-gradient(135deg, #007AFF 0%, #0056FF 100%);
    color: #fff;
    font-size: 34rpx;
    font-weight: 500;
    border-radius: 48rpx;
    margin-top: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    
    &[hover-class] {
      opacity: 0.9;
    }
  }
  
  .other-login {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 48rpx;
    
    .other-login-text {
      font-size: 24rpx;
      color: #999;
      margin-bottom: 24rpx;
    }
    
    .other-login-icons {
      display: flex;
      gap: 48rpx;
      
      .wechat-btn {
        padding: 16rpx;
      }
    }
  }
  
  .agreement {
    margin-top: 48rpx;
    display: flex;
    justify-content: center;
    
    .agreement-text {
      font-size: 24rpx;
      color: #999;
    }
    
    .link {
      font-size: 24rpx;
      color: #007AFF;
    }
  }
}
</style>
