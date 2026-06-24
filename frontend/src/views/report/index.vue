<template>
  <div class="page-report">
    <div class="page-toolbar">
      <h3>业务分析数据报表</h3>
      <el-button type="primary" @click="showDialog = true; formData = { ...emptyForm }">+ 新建报表任务</el-button>
    </div>

    <el-table :data="list" border stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="report_name" label="报表名称" min-width="140" />
      <el-table-column label="数据源" width="140">
        <template #default="{ row }">{{ sourceMap[row.source_id] || `ID:${row.source_id}` }}</template>
      </el-table-column>
      <el-table-column label="绑定菜单" width="140">
        <template #default="{ row }">{{ getMenuNameFromParams(row.crawl_params) }}</template>
      </el-table-column>
      <el-table-column prop="cron_expr" label="定时表达式" width="140" />
      <el-table-column prop="auto_push" label="自动推送" width="80">
        <template #default="{ row }">
          <el-tag :type="row.auto_push ? 'success' : 'info'">{{ row.auto_push ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="task_status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusMap[row.task_status] || 'info'">{{ row.task_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" :loading="crawlingId === row.id" @click="onReCrawl(row)">重新爬取</el-button>
          <el-button size="small" @click="onCronConfig(row)">定时配置</el-button>
          <el-button size="small" :disabled="!row.excel_file_path" @click="onPush(row)">立即推送</el-button>
          <el-button size="small" :disabled="!row.excel_file_path" @click="onDownload(row)">下载报表</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建弹窗 -->
    <el-dialog title="新建报表任务" v-model="showDialog" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="数据源" required>
          <el-select v-model="formData.source_id" style="width:100%" @change="onSourceChange">
            <el-option v-for="s in sources" :key="s.id" :label="s.source_name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="绑定菜单">
          <el-select v-model="formData.menu_code" clearable placeholder="可选绑定菜单" style="width:100%">
            <el-option v-for="m in sourceMenus" :key="m.menu_code" :label="m.menu_name" :value="m.menu_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表名称" required>
          <el-input v-model="formData.report_name" placeholder="如：月度销售数据报表" />
        </el-form-item>
        <el-form-item label="筛选参数">
          <el-input v-model="formData.extra_params" type="textarea" :rows="2" placeholder='可选额外参数, 如 {"date_from":"2026-01-01"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 定时配置弹窗 -->
    <el-dialog title="定时配置" v-model="showCronDialog" width="420px">
      <el-form :model="cronForm" label-width="100px">
        <el-form-item label="Cron表达式">
          <el-input v-model="cronForm.cron_expr" placeholder="0 8 * * 1-5 = 工作日8点" />
        </el-form-item>
        <el-form-item label="自动推送">
          <el-switch v-model="cronForm.auto_push" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCronDialog = false">取消</el-button>
        <el-button type="primary" :loading="cronSaving" @click="onSaveCron">保存</el-button>
      </template>
    </el-dialog>

    <!-- 全屏Loading遮罩 + 进度日志 -->
    <div v-if="fullLoading" class="full-loading">
      <div class="full-loading-box">
        <el-progress type="circle" :percentage="progressPercent" :status="progressStatus" />
        <pre class="progress-log">{{ progressLog }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const list = ref<any[]>([])
const sources = ref<any[]>([])
const sourceMenus = ref<any[]>([])
const sourceMap = ref<Record<number, string>>({})
const showDialog = ref(false)
const saving = ref(false)
const crawlingId = ref(0)
const fullLoading = ref(false)
const progressPercent = ref(0)
const progressLog = ref('')
const progressStatus = ref('')

const showCronDialog = ref(false)
const cronSaving = ref(false)
const cronForm = reactive({ cron_expr: '', auto_push: true })
const cronTaskId = ref(0)

const statusMap: Record<string, string> = { idle: 'info', running: 'warning', success: 'success', fail: 'danger' }

const emptyForm = { source_id: null, menu_code: '', report_name: '', extra_params: '{}' }
const formData = ref({ ...emptyForm, source_id: null as any, menu_code: '' })

let progressTimer: any = null

function getMenuNameFromParams(crawlParams: string): string {
  try {
    const cp = JSON.parse(crawlParams || '{}')
    if (cp.menu_code) {
      const m = sourceMenus.value.find((sm: any) => sm.menu_code === cp.menu_code)
      return m ? m.menu_name : cp.menu_code
    }
  } catch { /* ignore */ }
  return '-'
}

const onSourceChange = async (sourceId: number) => {
  try {
    const res: any = await request.get('/api/menu/list', { params: { source_id: sourceId } })
    sourceMenus.value = res.data || []
  } catch { sourceMenus.value = [] }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [reportRes, sourceRes]: any = await Promise.all([
      request.get('/api/report/list'),
      request.get('/api/source/list')
    ])
    list.value = reportRes.data || []
    sources.value = sourceRes.data || []
    sourceRes.data?.forEach((s: any) => { sourceMap.value[s.id] = s.source_name })
  } finally { loading.value = false }
}

const onCreate = async () => {
  saving.value = true
  try {
    // 组装 crawl_params：包含 menu_code + 额外参数
    const cp: any = {}
    if (formData.value.menu_code) cp.menu_code = formData.value.menu_code
    try {
      const extra = JSON.parse(formData.value.extra_params || '{}')
      Object.assign(cp, extra)
    } catch { /* ignore */ }

    const payload = {
      source_id: formData.value.source_id,
      report_name: formData.value.report_name,
      crawl_params: JSON.stringify(cp),
    }
    await request.post('/api/report/create', payload)
    ElMessage.success('创建成功')
    showDialog.value = false
    fetchData()
  } finally { saving.value = false }
}

const onReCrawl = async (row: any) => {
  crawlingId.value = row.id
  fullLoading.value = true
  progressPercent.value = 0
  progressLog.value = ''
  progressStatus.value = ''

  try {
    const res: any = await request.post(`/api/report/re-crawl/${row.id}`)
    const runId = res.run_id
    progressLog.value = '爬取任务已启动...\n'

    progressTimer = setInterval(async () => {
      try {
        const prog: any = await request.get(`/api/report/task-progress/${runId}`)
        progressLog.value = prog.log || progressLog.value
        if (prog.status === 'running') {
          progressPercent.value = Math.min(progressPercent.value + 10, 90)
          progressStatus.value = ''
        } else if (prog.status === 'success') {
          progressPercent.value = 100
          progressStatus.value = 'success'
          progressLog.value += '\n✅ 爬取完成！'
          clearInterval(progressTimer)
          setTimeout(() => { fullLoading.value = false; fetchData() }, 1500)
        } else if (prog.status === 'fail') {
          progressStatus.value = 'exception'
          progressLog.value += '\n❌ 爬取失败'
          clearInterval(progressTimer)
          setTimeout(() => { fullLoading.value = false; fetchData() }, 2000)
        }
      } catch { }
    }, 1000)
  } catch {
    crawlingId.value = 0
  } finally { crawlingId.value = 0 }
}

const onCronConfig = (row: any) => {
  cronTaskId.value = row.id
  cronForm.cron_expr = row.cron_expr || ''
  cronForm.auto_push = row.auto_push
  showCronDialog.value = true
}

const onSaveCron = async () => {
  cronSaving.value = true
  try {
    await request.post(`/api/report/cron-config/${cronTaskId.value}`, null, {
      params: { cron_expr: cronForm.cron_expr, auto_push: cronForm.auto_push }
    })
    ElMessage.success('定时配置已更新')
    showCronDialog.value = false; fetchData()
  } finally { cronSaving.value = false }
}

const onPush = async (row: any) => {
  try {
    const res: any = await request.post(`/api/report/push/${row.id}`)
    ElMessage[res.ok ? 'success' : 'warning'](res.msg)
  } catch { }
}

const onDownload = (row: any) => { window.open(row.excel_file_path, '_blank') }

onMounted(fetchData)
onUnmounted(() => { if (progressTimer) clearInterval(progressTimer) })
</script>

<style scoped>
.page-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-toolbar h3 { font-size: 18px; font-weight: 600; color: #333; }

.full-loading {
  position: fixed; inset: 0; background: rgba(255,255,255,0.92);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.full-loading-box {
  width: 420px; max-height: 80vh; background: #fff; border-radius: 16px;
  padding: 32px; box-shadow: 0 8px 40px rgba(0,0,0,0.12);
  text-align: center; display: flex; flex-direction: column; align-items: center; gap: 16px;
}
.progress-log {
  width: 100%; max-height: 300px; overflow-y: auto; text-align: left;
  font-size: 12px; color: #666; background: #f5f5f5; border-radius: 8px;
  padding: 12px; white-space: pre-wrap; line-height: 1.6; margin: 0;
}
</style>
