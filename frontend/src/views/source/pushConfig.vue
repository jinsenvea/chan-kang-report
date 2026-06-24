<template>
  <div class="page-push-config">
    <div class="page-toolbar">
      <h3>推送规则配置</h3>
      <el-button type="primary" @click="showDialog = true; isEdit = false; formData = { ...emptyForm }">+ 新增规则</el-button>
    </div>

    <el-table :data="list" border stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column label="数据源" min-width="140">
        <template #default="{ row }">{{ sourceMap[row.source_id] || `ID:${row.source_id}` }}</template>
      </el-table-column>
      <el-table-column prop="push_type" label="推送渠道" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.push_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_enable" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_enable ? 'success' : 'info'">{{ row.is_enable ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="onEdit(row)">编辑</el-button>
          <el-button size="small" :loading="testingId === row.id" @click="onTestPush(row)">测试推送</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="isEdit ? '编辑推送规则' : '新增推送规则'" v-model="showDialog" width="600px">
      <el-form :model="formData" label-width="120px">
        <el-form-item label="绑定数据源" required>
          <el-select v-model="formData.source_id" style="width:100%">
            <el-option v-for="s in sources" :key="s.id" :label="s.source_name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="推送渠道" required>
          <el-radio-group v-model="formData.push_type">
            <el-radio value="dingtalk">钉钉</el-radio>
            <el-radio value="feishu">飞书</el-radio>
            <el-radio value="wecom">企业微信</el-radio>
            <el-radio value="email">邮箱</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="配置内容">
          <el-input v-model="formData.config_json" type="textarea" :rows="6" placeholder='{"webhook":"https://...","secret":"..."}' />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="formData.is_enable" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const list = ref<any[]>([])
const sources = ref<any[]>([])
const sourceMap = ref<Record<number, string>>({})
const showDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref(0)
const testingId = ref(0)

const emptyForm = { source_id: null, push_type: 'dingtalk', config_json: '{}', is_enable: true }
const formData = ref({ ...emptyForm, source_id: null as any })

const fetchData = async () => {
  loading.value = true
  try {
    const [listRes, sourceRes]: any = await Promise.all([
      request.get('/api/push-config/list'),
      request.get('/api/source/list')
    ])
    list.value = listRes.data || []
    sources.value = sourceRes.data || []
    sourceMap.value = {}
    sourceRes.data?.forEach((s: any) => { sourceMap.value[s.id] = s.source_name })
  } finally { loading.value = false }
}

const onEdit = (row: any) => {
  isEdit.value = true; editId.value = row.id
  formData.value = { ...row }
  showDialog.value = true
}

const onSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await request.put(`/api/push-config/update/${editId.value}`, formData.value)
    } else {
      await request.post('/api/push-config/create', formData.value)
    }
    ElMessage.success('保存成功')
    showDialog.value = false; fetchData()
  } finally { saving.value = false }
}

const onTestPush = async (row: any) => {
  testingId.value = row.id
  try {
    const res: any = await request.post(`/api/push-config/test-push/${row.id}`)
    ElMessage[res.ok ? 'success' : 'error'](res.msg)
  } finally { testingId.value = 0 }
}

onMounted(fetchData)
</script>

<style scoped>
.page-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-toolbar h3 { font-size: 18px; font-weight: 600; color: #333; }
</style>
