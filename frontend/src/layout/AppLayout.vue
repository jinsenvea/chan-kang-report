<template>
  <div class="app-layout" :class="{ collapsed: appStore.sidebarCollapsed }">
    <Sidebar />
    <div class="layout-main">
      <Navbar />
      <div class="layout-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'

const appStore = useAppStore()
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--younger-sidebar-width);
  transition: margin-left 0.3s;
  background: var(--younger-bg);
}

.collapsed .layout-main {
  margin-left: var(--younger-sidebar-collapsed-width);
}

.layout-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
