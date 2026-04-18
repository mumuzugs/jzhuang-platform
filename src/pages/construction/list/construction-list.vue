<template>
  <view class="construction-list-container">
    <!-- 施工项目列表 -->
    <scroll-view 
      class="list-scroll" 
      scroll-y
      @scrolltolower="loadMore"
    >
      <view class="project-list">
        <view 
          v-for="item in projectList" 
          :key="item.id"
          class="project-card"
          @click="goToDetail(item.id)"
        >
          <!-- 项目头部 -->
          <view class="project-header">
            <view class="project-info">
              <text class="project-name">{{ item.name }}</text>
              <text class="project-address" v-if="item.address">{{ item.address }}</text>
            </view>
            <view :class="['status-tag', getStatusClass(item.status)]">
              {{ getStatusText(item.status) }}
            </view>
          </view>
          
          <!-- 进度条 -->
          <view class="progress-section">
            <view class="progress-header">
              <text class="progress-label">总体进度</text>
              <text class="progress-value">{{ item.progress }}%</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: item.progress + '%' }"></view>
            </view>
          </view>
          
          <!-- 节点概览 -->
          <view class="nodes-overview">
            <view 
              v-for="(node, index) in item.nodes?.slice(0, 4)" 
              :key="node.id"
              :class="['node-item', getNodeStatusClass(node.status)]"
            >
              <text class="node-name">{{ node.name }}</text>
            </view>
            <view class="node-item more" v-if="item.nodes?.length > 4">
              <text class="node-name">更多</text>
            </view>
          </view>
          
          <!-- 底部信息 -->
          <view class="project-footer">
            <text class="footer-text">工期 {{ item.total_cycle }} 天</text>
            <text class="footer-text" v-if="item.start_date">开始于 {{ formatDate(item.start_date) }}</text>
          </view>
        </view>
        
        <!-- 空状态 -->
        <view class="empty-state" v-if="projectList.length === 0 && !loading">
          <text class="empty-icon">👷</text>
          <text class="empty-text">暂无施工项目</text>
          <button class="start-btn" @click="createProject">创建项目</button>
        </view>
        
        <!-- 加载状态 -->
        <view class="loading-more" v-if="loading">
          <text>加载中...</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 创建项目按钮 -->
    <view class="bottom-action" v-if="projectList.length > 0">
      <button class="action-btn" @click="createProject">新建项目</button>
    </view>
    <!-- 底部 TabBar -->
    <TabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import TabBar from '@/components/TabBar.vue'
import { getProjectList, type ConstructionProject } from '@/api/construction'

const projectList = ref<ConstructionProject[]>([])
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
    projectList.value = []
  }
  
  try {
    const res = await getProjectList({ page: page.value, page_size: 10 })
    projectList.value = reset ? res.projects : [...projectList.value, ...res.projects]
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value++
  fetchList()
}

function goToDetail(id: string) {
  uni.navigateTo({ url: `/pages/construction/detail/construction-detail?id=${id}` })
}

function createProject() {
  uni.navigateTo({ url: '/pages/construction/create/create-construction' })
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function getStatusClass(status: string) {
  const map: Record<string, string> = {
    pending: 'pending',
    in_progress: 'progress',
    completed: 'completed',
    paused: 'paused',
  }
  return map[status] || 'pending'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待开工',
    in_progress: '进行中',
    completed: '已完成',
    paused: '已暂停',
  }
  return map[status] || '未知'
}

function getNodeStatusClass(status: string) {
  const map: Record<string, string> = {
    completed: 'completed',
    in_progress: 'progress',
    pending: 'pending',
    delayed: 'delayed',
  }
  return map[status] || 'pending'
}
</script>

<style lang="scss" scoped>
.construction-list-container {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  padding-bottom: 100rpx;
}

.list-scroll {
  flex: 1;
  padding: 24rpx 32rpx;
}

.project-list {
  .project-card {
    background: #fff;
    border-radius: 16rpx;
    padding: 28rpx;
    margin-bottom: 24rpx;
    
    .project-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24rpx;
      
      .project-info {
        flex: 1;
        
        .project-name {
          font-size: 32rpx;
          font-weight: 600;
          color: #333;
          display: block;
          margin-bottom: 8rpx;
        }
        
        .project-address {
          font-size: 26rpx;
          color: #999;
        }
      }
      
      .status-tag {
        font-size: 24rpx;
        padding: 8rpx 16rpx;
        border-radius: 8rpx;
        
        &.pending { color: #999; background: #f5f5f5; }
        &.progress { color: #007AFF; background: #E8F4FF; }
        &.completed { color: #52c41a; background: #f6ffed; }
        &.paused { color: #faad14; background: #fffbe6; }
      }
    }
    
    .progress-section {
      margin-bottom: 24rpx;
      
      .progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12rpx;
        
        .progress-label {
          font-size: 26rpx;
          color: #666;
        }
        
        .progress-value {
          font-size: 28rpx;
          font-weight: 600;
          color: #007AFF;
        }
      }
      
      .progress-bar {
        height: 8rpx;
        background: #f0f0f0;
        border-radius: 4rpx;
        
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #007AFF 0%, #0056FF 100%);
          border-radius: 4rpx;
          transition: width 0.3s;
        }
      }
    }
    
    .nodes-overview {
      display: flex;
      flex-wrap: wrap;
      gap: 16rpx;
      margin-bottom: 24rpx;
      
      .node-item {
        padding: 12rpx 20rpx;
        border-radius: 8rpx;
        background: #f5f5f5;
        
        .node-name {
          font-size: 24rpx;
          color: #666;
        }
        
        &.completed {
          background: #f6ffed;
          .node-name { color: #52c41a; }
        }
        
        &.progress {
          background: #E8F4FF;
          .node-name { color: #007AFF; }
        }
        
        &.delayed {
          background: #fff2f0;
          .node-name { color: #ff4d4f; }
        }
        
        &.more {
          background: #fafafa;
          .node-name { color: #999; }
        }
      }
    }
    
    .project-footer {
      display: flex;
      justify-content: space-between;
      padding-top: 20rpx;
      border-top: 1rpx solid #f0f0f0;
      
      .footer-text {
        font-size: 24rpx;
        color: #999;
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
