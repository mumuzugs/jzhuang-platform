<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { useUserStore } from '@/store/user'

onLaunch(() => {
  console.log('App Launch')
  
  // 初始化应用状态
  const appStore = useAppStore()
  appStore.init()
  
  // 初始化用户状态
  const userStore = useUserStore()
  userStore.init()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
@import '@/styles/index.scss';
</style>
