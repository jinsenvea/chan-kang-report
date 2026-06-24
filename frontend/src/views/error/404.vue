<template>
  <div class="page-404">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/source/list')">返回首页</el-button>
  </div>
</template>

<style scoped>
.page-404 { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.page-404 h1 { font-size: 72px; color: #1677FF; margin-bottom: 12px; }
.page-404 p { font-size: 16px; color: #999; margin-bottom: 24px; }
</style>
