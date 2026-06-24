<template>
  <div class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="sidebar-logo">
      <span class="logo-icon">P</span>
      <span v-show="!appStore.sidebarCollapsed" class="logo-text">PeerBizSync</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="appStore.sidebarCollapsed"
      :router="true"
      background-color="#001529"
      text-color="#ffffffa6"
      active-text-color="#1677FF"
    >
      <template v-for="item in mergedMenu" :key="item.id">
        <el-menu-item v-if="!item.children || item.children.length === 0" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.name }}</template>
        </el-menu-item>
        <el-sub-menu v-else :index="item.path">
          <template #title>
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.name }}</span>
          </template>
          <el-menu-item v-for="child in item.children" :key="child.id" :index="child.path">
            {{ child.name }}
          </el-menu-item>
        </el-sub-menu>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { menuList, MenuItem } from '@/config/menu'
import request from '@/utils/request'

const route = useRoute()
const appStore = useAppStore()
const dynamicMenus = ref<{ id: number; menu_code: string; menu_name: string }[]>([])

const mergedMenu = computed(() => {
  const clone = JSON.parse(JSON.stringify(menuList)) as MenuItem[]
  // 在「原始数据源数据列表」(id=2) 下追加动态菜单
  const rawDataItem = clone.find(m => m.id === 2)
  if (rawDataItem && rawDataItem.children) {
    rawDataItem.children = [
      ...rawDataItem.children.filter(c => !c.dynamic),
      ...dynamicMenus.value.map((m, idx) => ({
        id: 200 + idx,
        name: m.menu_name,
        path: `/raw-data/${m.menu_code}`,
        dynamic: true,
      })),
    ]
  }
  return clone
})

const activeMenu = computed(() => route.path)

onMounted(async () => {
  try {
    const res: any = await request.get('/api/menu/list')
    dynamicMenus.value = (res.data || []).map((m: any) => ({
      id: m.id,
      menu_code: m.menu_code,
      menu_name: m.menu_name,
    }))
  } catch {
    // 静默失败，菜单为空不影响使用
  }
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--younger-sidebar-width);
  background: #001529;
  transition: width 0.3s;
  z-index: 100;
  overflow: hidden;
}
.sidebar.collapsed { width: var(--younger-sidebar-collapsed-width); }
.sidebar-logo {
  height: 56px; display: flex; align-items: center; justify-content: center; gap: 10px;
  background: linear-gradient(135deg, #1677FF, #0F58C9); color: #fff;
  font-weight: 700; font-size: 16px; overflow: hidden; white-space: nowrap;
}
.logo-icon {
  width: 32px; height: 32px; border-radius: 8px; background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
}
.logo-text { letter-spacing: 1px; }
.el-menu { border-right: none; }
</style>
