<template>
  <div class="page-raw-data">
    <div class="page-toolbar">
      <h3>原始数据源数据列表</h3>
      <div class="toolbar-actions">
        <!-- 菜单切换下拉：跳转动态独立页面 -->
        <el-select v-model="selectedMenuCode" placeholder="切换至菜单专属页面" clearable style="width:200px" @change="onMenuChange">
          <el-option v-for="m in allMenus" :key="m.menu_code" :label="m.menu_name" :value="m.menu_code" />
        </el-select>
        <el-select v-model="filters.source_id" placeholder="数据源" clearable style="width:160px">
          <el-option v-for="s in sources" :key="s.id" :label="s.source_name" :value="s.id" />
        </el-select>
        <el-select v-model="filters.menu_code" placeholder="菜单筛选" clearable style="width:160px">
          <el-option v-for="m in allMenus" :key="m.menu_code" :label="m.menu_name" :value="m.menu_code" />
        </el-select>
        <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:260px" />
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="onExport">导出Excel</el-button>
      </div>
    </div>

    <el-table :data="list" border stripe v-loading="loading" style="width:100%" max-height="600px">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="source_id" label="数据源ID" width="80" />
      <el-table-column prop="menu_code" label="菜单编码" width="120" />
      <el-table-column label="原始数据" min-width="300" show-overflow-tooltip>
        <template #default="{ row }">
          <pre style="margin:0; font-size:11px; max-height:60px; overflow:hidden;">{{ row.raw_json }}</pre>
        </template>
      </el-table-column>
      <el-table-column prop="crawl_time" label="抓取时间" width="180" />
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const sources = ref<any[]>([])
const allMenus = ref<any[]>([])
const selectedMenuCode = ref('')

const filters = reactive({
  source_id: null as number | null,
  menu_code: null as string | null,
  dateRange: null as string[] | null,
})

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.source_id) params.source_id = filters.source_id
    if (filters.menu_code) params.menu_code = filters.menu_code
    if (filters.dateRange) { params.date_from = filters.dateRange[0]; params.date_to = filters.dateRange[1] }
    const res: any = await request.get('/api/raw-data/list', { params })
    list.value = res.data || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

const onExport = async () => {
  try {
    const params: any = {}
    if (filters.source_id) params.source_id = filters.source_id
    if (filters.menu_code) params.menu_code = filters.menu_code
    if (filters.dateRange) { params.date_from = filters.dateRange[0]; params.date_to = filters.dateRange[1] }
    const res: any = await request.get('/api/raw-data/export', { params })
    ElMessage[res.ok ? 'success' : 'warning'](res.msg)
  } catch { }
}

const onMenuChange = (code: string) => {
  if (code) router.push(`/raw-data/${code}`)
}

onMounted(async () => {
  const [sourceRes, menuRes]: any = await Promise.all([
    request.get('/api/source/list'),
    request.get('/api/menu/list')
  ])
  sources.value = sourceRes.data || []
  allMenus.value = menuRes.data || []
  fetchData()
})
</script>

<style scoped>
.page-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.page-toolbar h3 { font-size: 18px; font-weight: 600; color: #333; margin: 0; }
.toolbar-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.pagination-bar { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
