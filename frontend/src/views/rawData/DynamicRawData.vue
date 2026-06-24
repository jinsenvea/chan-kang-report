<template>
  <div class="page-raw-data">
    <div class="page-toolbar">
      <h3>{{ menuName || '数据加载中...' }}</h3>
      <div class="toolbar-actions">
        <!-- 动态筛选控件：根据 filter_schema 自动渲染 -->
        <template v-for="(f, i) in filterFields" :key="i">
          <el-input
            v-if="f.type === 'input'"
            v-model="dynamicFilters[f.field]"
            :placeholder="f.label"
            clearable
            style="width:140px"
          />
          <el-select
            v-if="f.type === 'select'"
            v-model="dynamicFilters[f.field]"
            :placeholder="f.label"
            clearable
            style="width:140px"
          >
            <el-option v-for="opt in (f.options || [])" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-date-picker
            v-if="f.type === 'date'"
            v-model="dynamicFilters[f.field]"
            type="date"
            :placeholder="f.label"
            value-format="YYYY-MM-DD"
            style="width:140px"
          />
        </template>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:240px" />
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="onExport">导出Excel</el-button>
      </div>
    </div>

    <el-table :data="list" border stripe v-loading="loading" style="width:100%" max-height="600px">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="原始数据" min-width="400" show-overflow-tooltip>
        <template #default="{ row }">
          <pre style="margin:0; font-size:11px; max-height:80px; overflow-y:auto;">{{ row.raw_json }}</pre>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const menuCode = computed(() => route.params.menuCode as string)

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const menuName = ref('')
const filterFields = ref<any[]>([])
const dynamicFilters = reactive<Record<string, any>>({})
const dateRange = ref<string[] | null>(null)

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {
      menu_code: menuCode.value,
      page: page.value,
      page_size: pageSize.value,
    }
    // 动态筛选参数
    for (const f of filterFields.value) {
      const val = dynamicFilters[f.field]
      if (val !== undefined && val !== null && val !== '') {
        params[`filter_${f.field}`] = val
      }
    }
    if (dateRange.value) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const res: any = await request.get('/api/raw-data/list', { params })
    list.value = res.data || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

const onExport = async () => {
  try {
    const params: any = { menu_code: menuCode.value }
    if (dateRange.value) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    const res: any = await request.get('/api/raw-data/export', { params })
    ElMessage[res.ok ? 'success' : 'warning'](res.msg)
  } catch { /* ignore */ }
}

onMounted(async () => {
  try {
    const res: any = await request.get(`/api/menu/detail/${menuCode.value}`)
    menuName.value = res.menu_name || menuCode.value
    const schema = JSON.parse(res.filter_schema || '[]')
    filterFields.value = schema.map((item: any) => ({
      field: item.field,
      label: item.label || item.field,
      type: item.type || 'input',
      options: item.options || [],
    }))
    // 初始化筛选控件默认值
    for (const f of filterFields.value) {
      if (dynamicFilters[f.field] === undefined) {
        dynamicFilters[f.field] = ''
      }
    }
  } catch {
    menuName.value = menuCode.value
  }
  fetchData()
})
</script>

<style scoped>
.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.page-toolbar h3 { font-size: 18px; font-weight: 600; color: #333; margin: 0; }
.toolbar-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.pagination-bar { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
