<template>
  <view class="design-list-container">
    <!-- 顶部 Tab -->
    <view class="tabs">
      <view 
        v-for="tab in tabs" 
        :key="tab.value"
        :class="['tab-item', { active: currentTab === tab.value }]"
        @click="onTabChange(tab.value)"
      >
        {{ tab.label }}
      </view>
    </view>
    
    <!-- 设计列表 -->
    <scroll-view 
      class="list-scroll" 
      scroll-y
      @scrolltolower="loadMore"
    >
      <view class="design-list">
        <view 
          v-for="item in designList" 
          :key="item.id"
          class="design-card"
          @click="goToDetail(item.id)"
        >
          <image 
            class="design-cover" 
            :src="item.cover_image || '/static/default-design.jpg'" 
            mode="aspectFill" 
          />
          <view class="design-info">
            <view class="design-header">
              <text class="design-name">{{ item.name || '设计方案' }}</text>
              <text class="design-date">{{ formatDate(item.created_at) }}</text>
            </view>
            <view class="design-meta">
              <text class="meta-item">{{ item.area }}㎡</text>
              <text class="meta-divider">|</text>
              <text class="meta-item">{{ getStyleName(item.style) }}</text>
            </view>
            <view class="design-budget">
              <text class="budget-label">预估预算：</text>
              <text class="budget-value">¥{{ item.budget_range || '--' }}</text>
            </view>
          </view>
        </view>
        
        <!-- 空状态 -->
        <view class="empty-state" v-if="designList.length === 0 && !loading">
          <text class="empty-icon">🎨</text>
          <text class="empty-text">暂无设计方案</text>
          <button class="start-btn" @click="startDesign">开始设计</button>
        </view>
        
        <!-- 加载状态 -->
        <view class="loading-more" v-if="loading">
          <text>加载中...</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 开始设计按钮 -->
    <view class="bottom-action" v-if="designList.length > 0">
      <button class="action-btn" @click="startDesign">新建方案</button>
    </view>
    <!-- 底部 TabBar -->
    <TabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import TabBar from '@/components/TabBar.vue'
import { getDesignList, type Style } from '@/api/design'

const tabs = [
  { label: '全部', value: 'all' },
  { label: '我的', value: 'my' },
]

const currentTab = ref('all')
const designList = ref<any[]>([])
const styles = ref<Style[]>([])
const loading = ref(false)
const page = ref(1)

onMounted(() => {
  fetchList()
})

async function fetchList(reset = false) {
  if (loading.value) return
  
  loading.value = true
  if (reset) {
    page.value = 1
    designList.value = []
  }
  
  try {
    const res = await getDesignList({ page: page.value, page_size: 10 })
    designList.value = reset ? res.designs : [...designList.value, ...res.designs]
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function onTabChange(value: string) {
  currentTab.value = value
  fetchList(true)
}

function loadMore() {
  page.value++
  fetchList()
}

function goToDetail(id: string) {
  uni.navigateTo({ url: `/pages/design/result/design-result?id=${id}` })
}

function startDesign() {
  uni.navigateTo({ url: '/pages/design/create/create-design' })
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function getStyleName(styleCode: string) {
  const style = styles.value.find(s => s.code === styleCode)
  return style?.name || styleCode || '现代简约'
}
</script>

<style lang="scss" scoped>
.design-list-container {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  padding-bottom: 100rpx;
}

.tabs {
  display: flex;
  background: #fff;
  padding: 0 32rpx;
  
  .tab-item {
    flex: 1;
    height: 88rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    color: #666;
    position: relative;
    
    &.active {
      color: #007AFF;
      font-weight: 500;
      
      &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 48rpx;
        height: 4rpx;
        background: #007AFF;
        border-radius: 2rpx;
      }
    }
  }
}

.list-scroll {
  flex: 1;
  padding: 24rpx 32rpx;
}

.design-list {
  .design-card {
    background: #fff;
    border-radius: 16rpx;
    overflow: hidden;
    margin-bottom: 24rpx;
    
    .design-cover {
      width: 100%;
      height: 400rpx;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .design-info {
      padding: 24rpx;
      
      .design-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12rpx;
        
        .design-name {
          font-size: 32rpx;
          font-weight: 600;
          color: #333;
        }
        
        .design-date {
          font-size: 24rpx;
          color: #999;
        }
      }
      
      .design-meta {
        display: flex;
        align-items: center;
        margin-bottom: 16rpx;
        
        .meta-item {
          font-size: 26rpx;
          color: #666;
        }
        
        .meta-divider {
          color: #ddd;
          margin: 0 16rpx;
        }
      }
      
      .design-budget {
        display: flex;
        align-items: baseline;
        
        .budget-label {
          font-size: 26rpx;
          color: #999;
        }
        
        .budget-value {
          font-size: 32rpx;
          font-weight: 600;
          color: #ff4d4f;
        }
      }
    }
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 100rpx 0;
    
    .empty-icon {
      font-size: 120rpx;
      margin-bottom: 32rpx;
    }
    
    .empty-text {
      font-size: 28rpx;
      color: #999;
      margin-bottom: 48rpx;
    }
    
    .start-btn {
      width: 240rpx;
      height: 80rpx;
      background: linear-gradient(135deg, #007AFF 0%, #0056FF 100%);
      color: #fff;
      font-size: 30rpx;
      border-radius: 40rpx;
      border: none;
    }
  }
  
  .loading-more {
    text-align: center;
    padding: 24rpx 0;
    
    text {
      font-size: 24rpx;
      color: #999;
    }
  }
}

.bottom-action {
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
  
  .action-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #007AFF 0%, #0056FF 100%);
    color: #fff;
    font-size: 32rpx;
    font-weight: 500;
    border-radius: 44rpx;
    border: none;
  }
}
</style>
