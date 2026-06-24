<template>
  <div class="page-source-list">
    <div class="page-toolbar">
      <h3>数据源列表</h3>
      <el-button type="primary" @click="showDialog = true; isEdit = false; formData = { ...emptyForm }">+ 新增数据源</el-button>
    </div>

    <el-table :data="list" border stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="source_name" label="渠道名称" min-width="140" />
      <el-table-column prop="base_url" label="平台根地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="account" label="账号" width="140" />
      <el-table-column prop="client_type" label="客户端类型" width="120" />
      <el-table-column prop="page_size" label="分页条数" width="80" />
      <el-table-column prop="enable" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enable ? 'success' : 'info'">{{ row.enable ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="onEdit(row)">编辑</el-button>
          <el-button size="small" :loading="testingId === row.id" @click="onTestConnect(row)">测试连接</el-button>
          <el-button size="small" type="success" @click="onManageMenus(row)">管理菜单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑数据源弹窗 -->
    <el-dialog :title="isEdit ? '编辑数据源' : '新增数据源'" v-model="showDialog" width="600px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="渠道名称" required>
          <el-input v-model="formData.source_name" placeholder="如：K3Cloud生产环境" />
        </el-form-item>
        <el-form-item label="平台根地址" required>
          <el-input v-model="formData.base_url" placeholder="https://your-k3cloud-instance.com" />
        </el-form-item>
        <el-form-item label="账号" required>
          <el-input v-model="formData.account" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="formData.password" type="password" show-password :placeholder="isEdit ? '留空则不修改' : ''" />
        </el-form-item>
        <el-form-item label="客户端类型">
          <el-input v-model="formData.client_type" placeholder="如：K3Cloud" />
        </el-form-item>
        <el-form-item label="登录接口">
          <el-input v-model="formData.login_api" placeholder="/api/login" />
        </el-form-item>
        <el-form-item label="数据接口">
          <el-input v-model="formData.data_api" placeholder="/api/data/list" />
        </el-form-item>
        <el-form-item label="分页条数">
          <el-input-number v-model="formData.page_size" :min="10" :max="1000" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="formData.enable" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 管理菜单弹窗 -->
    <el-dialog title="管理抓取菜单" v-model="showMenuDialog" width="700px">
      <div style="margin-bottom:12px">
        <el-button type="primary" size="small" @click="onAddMenu">+ 新增菜单</el-button>
        <span style="color:#999;font-size:12px;margin-left:10px">在此处新增平台菜单，系统将自动生成独立数据页面</span>
      </div>
      <el-table :data="menuList" border stripe style="width:100%">
        <el-table-column prop="menu_code" label="菜单编码" width="140" />
        <el-table-column prop="menu_name" label="菜单名称" min-width="140" />
        <el-table-column prop="list_api" label="列表接口" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{ row, $index }">
            <el-button size="small" @click="onEditMenu($index)">编辑</el-button>
            <el-button size="small" type="danger" @click="onDeleteMenu($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 新增/编辑菜单弹窗 -->
    <el-dialog :title="isEditMenu ? '编辑菜单' : '新增菜单'" v-model="showMenuFormDialog" width="600px">
      <el-form :model="menuForm" label-width="120px">
        <el-form-item label="菜单编码" required>
          <el-input v-model="menuForm.menu_code" placeholder="唯一编码，如：order_detail" :disabled="isEditMenu" />
        </el-form-item>
        <el-form-item label="菜单名称" required>
          <el-input v-model="menuForm.menu_name" placeholder="如：营业明细" />
        </el-form-item>
        <el-form-item label="列表接口">
          <el-input v-model="menuForm.list_api" placeholder="如：/api/order/list" />
        </el-form-item>
        <el-form-item label="导出接口">
          <el-input v-model="menuForm.export_api" placeholder="如：/api/order/export" />
        </el-form-item>
        <el-form-item label="筛选字段定义">
          <el-input v-model="menuForm.filter_schema" type="textarea" :rows="4"
            placeholder='[{"field":"store_id","label":"门店","type":"select","options":[{"label":"全部","value":"all"}]}]' />
        </el-form-item>
        <el-form-item label="分页参数">
          <el-input v-model="menuForm.page_param" placeholder='{"page_field":"page","size_field":"page_size"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMenuFormDialog = false">取消</el-button>
        <el-button type="primary" @click="onSaveMenu">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

interface DataSource {
  id: number; source_name: string; base_url: string; account: string;
  client_type: string; login_api: string; data_api: string;
  page_size: number; enable: boolean; password?: string;
}

const loading = ref(false)
const list = ref<DataSource[]>([])
const showDialog = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref(0)
const testingId = ref(0)

// 菜单管理
const showMenuDialog = ref(false)
const showMenuFormDialog = ref(false)
const isEditMenu = ref(false)
const editMenuIdx = ref(-1)
const currentSourceId = ref(0)
const menuList = ref<any[]>([])
const menuForm = ref({
  menu_code: '', menu_name: '', list_api: '', export_api: '',
  filter_schema: '[]', page_param: '{}',
})

const emptyForm = { source_name: '', base_url: '', account: '', password: '', client_type: '', login_api: '', data_api: '', page_size: 100, enable: true }
const formData = ref<DataSource>({ ...emptyForm } as any)

const fetchList = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/api/source/list')
    list.value = res.data || []
  } finally { loading.value = false }
}

const onEdit = (row: DataSource) => {
  isEdit.value = true; editId.value = row.id
  formData.value = { ...row, password: '' }
  showDialog.value = true
}

const onSave = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await request.put(`/api/source/update/${editId.value}`, formData.value)
    } else {
      await request.post('/api/source/create', formData.value)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
    showDialog.value = false
    fetchList()
  } finally { saving.value = false }
}

const onTestConnect = async (row: DataSource) => {
  // 如果表单打开且匹配当前行，用表单里的密码
  let pwd = ''
  if (showDialog.value && editId.value === row.id && formData.value.password) {
    pwd = formData.value.password
  } else {
    // 弹窗让用户输入密码
    const { value } = await ElMessageBox.prompt('请输入数据源密码进行连通性测试', '密码验证', {
      inputType: 'password', confirmButtonText: '测试', cancelButtonText: '取消'
    }).catch(() => ({ value: '' }))
    pwd = value || ''
  }
  testingId.value = row.id
  try {
    const res: any = await request.post(`/api/source/test-connect/${row.id}`, { password: pwd })
    ElMessage[res.ok ? 'success' : 'error'](res.msg)
  } finally { testingId.value = 0 }
}

// 菜单管理
const onManageMenus = async (row: DataSource) => {
  currentSourceId.value = row.id
  try {
    const res: any = await request.get('/api/menu/list', { params: { source_id: row.id } })
    menuList.value = (res.data || []).map((m: any) => ({
      id: m.id, menu_code: m.menu_code, menu_name: m.menu_name,
      list_api: m.list_api, export_api: m.export_api,
      filter_schema: m.filter_schema, page_param: m.page_param,
    }))
  } catch {
    menuList.value = []
  }
  showMenuDialog.value = true
}

const onAddMenu = () => {
  isEditMenu.value = false; editMenuIdx.value = -1
  menuForm.value = { menu_code: '', menu_name: '', list_api: '', export_api: '', filter_schema: '[]', page_param: '{}' }
  showMenuFormDialog.value = true
}

const onEditMenu = (idx: number) => {
  isEditMenu.value = true; editMenuIdx.value = idx
  const m = menuList.value[idx]
  menuForm.value = {
    menu_code: m.menu_code, menu_name: m.menu_name, list_api: m.list_api || '',
    export_api: m.export_api || '', filter_schema: m.filter_schema || '[]',
    page_param: m.page_param || '{}',
  }
  showMenuFormDialog.value = true
}

const onSaveMenu = async () => {
  try {
    const payload = { ...menuForm.value, source_id: currentSourceId.value }
    if (isEditMenu.value) {
      const m = menuList.value[editMenuIdx.value]
      await request.put(`/api/menu/update/${m.id}`, payload)
    } else {
      await request.post('/api/menu/create', payload)
    }
    ElMessage.success(isEditMenu.value ? '菜单已更新' : '菜单已新增')
    showMenuFormDialog.value = false
    // 刷新列表
    const res: any = await request.get('/api/menu/list', { params: { source_id: currentSourceId.value } })
    menuList.value = (res.data || []).map((m: any) => ({
      id: m.id, menu_code: m.menu_code, menu_name: m.menu_name,
      list_api: m.list_api, export_api: m.export_api,
      filter_schema: m.filter_schema, page_param: m.page_param,
    }))
  } catch { }
}

const onDeleteMenu = async (idx: number) => {
  try {
    const m = menuList.value[idx]
    await request.delete(`/api/menu/delete/${m.id}`)
    ElMessage.success('菜单已删除')
    menuList.value.splice(idx, 1)
  } catch { }
}

onMounted(fetchList)
</script>

<style scoped>
.page-source-list { }
.page-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-toolbar h3 { font-size: 18px; font-weight: 600; color: #333; }
</style>
