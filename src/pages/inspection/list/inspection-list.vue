<template>
  <view class="inspection-list-container">
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
    
    <!-- 验房项目列表 -->
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
          <view class="project-header">
            <view class="project-info">
              <text class="project-name">{{ item.house_type }}</text>
              <text class="project-date">{{ formatDate(item.created_at) }}</text>
            </view>
            <view :class="['status-tag', getStatusClass(item.report)]">
              {{ item.report ? '已完成' : '处理中' }}
            </view>
          </view>
          
          <view class="project-content" v-if="item.report">
            <view class="stats-row">
              <view class="stat-item">
                <text class="stat-value">{{ item.report.issue_count }}</text>
                <text class="stat-label">发现问题</text>
              </view>
              <view class="stat-item">
                <text class="stat-value warning">{{ item.report.high_risk_count }}</text>
                <text class="stat-label">高风险</text>
              </view>
              <view class="stat-item">
                <text class="stat-value">{{ item.report.total_estimated_cost }}</text>
                <text class="stat-label">预估费用</text>
              </view>
            </view>
          </view>
          
          <view class="project-tip" v-else>
            <text>AI 正在分析中，请稍候...</text>
          </view>
        </view>
        
        <!-- 空状态 -->
        <view class="empty-state" v-if="projectList.length === 0 && !loading">
          <text class="empty-icon">🏠</text>
          <text class="empty-text">暂无验房记录</text>
          <button class="start-btn" @click="startInspection">开始验房</button>
        </view>
        
        <!-- 加载状态 -->
        <view class="loading-more" v-if="loading">
          <text>加载中...</text>
        </view>
        
        <!-- 没有更多 -->
        <view class="no-more" v-if="!hasMore && projectList.length > 0">
          <text>没有更多了</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 开始验房按钮 -->
    <view class="bottom-action" v-if="projectList.length > 0">
      <button class="action-btn" @click="startInspection">新建验房</button>
    </view>
    <!-- 底部 TabBar -->
    <TabBar />
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import TabBar from '@/components/TabBar.vue'
import { getInspectionList, type InspectionProject } from '@/api/inspection'

const tabs = [
  { label: '全部', value: 'all' },
  { label: '已完成', value: 'completed' },
  { label: '处理中', value: 'processing' },
]

const currentTab = ref('all')
const projectList = ref<InspectionProject[]>([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)

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
    const params: any = { page: page.value, page_size: 10 }
    const res = await getInspectionList(params)
    
    if (currentTab.value === 'completed') {
      projectList.value = res.projects.filter(p => p.report)
    } else if (currentTab.value === 'processing') {
      projectList.value = res.projects.filter(p => !p.report)
    } else {
      projectList.value = reset ? res.projects : [...projectList.value, ...res.projects]
    }
    
    hasMore.value = res.projects.length >= 10
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
  if (hasMore.value && !loading.value) {
    page.value++
    fetchList()
  }
}

function goToDetail(id: string) {
  uni.navigateTo({ url: `/pages/inspection/detail/inspection-detail?id=${id}` })
}

function startInspection() {
  // 选择房屋类型
  uni.showActionSheet({
    itemList: ['毛坯房', '二手房'],
    success: (res) => {
      const houseType = res.tapIndex === 0 ? '毛坯房' : '二手房'
      uni.navigateTo({
        url: `/pages/inspection/create/create-inspection?house_type=${houseType}`
      })
    }
  })
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function getStatusClass(report: any) {
  return report ? 'completed' : 'processing'
}
</script>

<style lang="scss" scoped>
.inspection-list-container {
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
      margin-bottom: 20rpx;
      
      .project-info {
        display: flex;
        flex-direction: column;
        
        .project-name {
          font-size: 32rpx;
          font-weight: 600;
          color: #333;
          margin-bottom: 8rpx;
        }
        
        .project-date {
          font-size: 24rpx;
          color: #999;
        }
      }
      
      .status-tag {
        font-size: 24rpx;
        padding: 8rpx 16rpx;
        border-radius: 8rpx;
        
        &.completed {
          color: #52c41a;
          background: #f6ffed;
        }
        
        &.processing {
          color: #faad14;
          background: #fffbe6;
        }
      }
    }
    
    .project-content {
      .stats-row {
        display: flex;
        justify-content: space-around;
        
        .stat-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          
          .stat-value {
            font-size: 36rpx;
            font-weight: 600;
            color: #333;
            
            &.warning {
              color: #ff4d4f;
            }
          }
          
          .stat-label {
            font-size: 24rpx;
            color: #999;
            margin-top: 4rpx;
          }
        }
      }
    }
    
    .project-tip {
      text-align: center;
      padding: 20rpx 0;
      
      text {
        font-size: 26rpx;
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
      display: flex;
      align-items: center;
      justify-content: center;
      border: none;
    }
  }
  
  .loading-more,
  .no-more {
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
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
  }
}
</style>
