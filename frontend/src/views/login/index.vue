<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="login-brand">
        <div class="brand-logo">
          <span class="brand-icon">P</span>
          <span class="brand-name">PeerBizSync</span>
        </div>
        <h2 class="brand-title">产康数据报表系统</h2>
        <p class="brand-desc">K3Cloud 数据爬取 · 报表生成 · 多渠道自动推送<br/>高效 精准 自动化</p>
        <div class="brand-features">
          <div class="feature-item">✅ 多平台数据源统一管理</div>
          <div class="feature-item">📊 标准化 Excel 报表自动生成</div>
          <div class="feature-item">📤 钉钉/飞书/企微/邮件多渠道推送</div>
          <div class="feature-item">⏱️ 定时任务全自动化执行</div>
        </div>
      </div>
      <div class="login-form-wrap">
        <div class="login-form-box">
          <div class="demo-badge">
            <el-tag type="success" size="small" effect="dark">🎮 演示模式</el-tag>
            <p class="demo-tip">无需后端服务，一键体验全部页面</p>
          </div>
          <el-button
            size="large"
            class="demo-login-btn"
            :loading="demoLoading"
            @click="handleDemoLogin"
          >
            🎮 演示登录 — 立即体验
          </el-button>
          <div class="divider"><span>或</span></div>
          <h3 class="form-title">账号登录</h3>
          <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
            <el-form-item prop="username">
              <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">登 录</el-button>
            </el-form-item>
          </el-form>
          <div class="login-footer">© 2026 产康数据报表系统. All rights reserved.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { setDemoMode } from '@/utils/auth'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const demoLoading = ref(false)

const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push('/source/list')
  } catch (e: any) {
    // 错误已在 request.ts 中处理
  } finally {
    loading.value = false
  }
}

const handleDemoLogin = async () => {
  demoLoading.value = true
  try {
    setDemoMode(true)
    userStore.demoLogin()
    ElMessage.success('🎮 演示模式 — 已登录，所有数据为模拟展示')
    router.push('/source/list')
  } finally {
    demoLoading.value = false
  }
}
</script>

<style scoped>
.login-page { height: 100vh; display: flex; }
.login-bg { display: flex; width: 100%; height: 100%; }

.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #1677FF 0%, #0F58C9 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.brand-logo { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; }
.brand-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; }
.brand-name { font-size: 24px; font-weight: 700; letter-spacing: 1px; }
.brand-title { font-size: 28px; font-weight: 700; margin-bottom: 12px; }
.brand-desc { font-size: 14px; opacity: 0.8; margin-bottom: 40px; line-height: 1.8; }
.brand-features { display: flex; flex-direction: column; gap: 12px; }
.feature-item { font-size: 14px; opacity: 0.9; }

.login-form-wrap {
  width: 440px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
}

.login-form-box { width: 340px; }
.form-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 20px; text-align: center; }

.demo-badge { text-align: center; margin-bottom: 12px; }
.demo-badge .demo-tip { font-size: 12px; color: #999; margin-top: 6px; }

.demo-login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #67C23A, #529B2E);
  border: none;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
}
.demo-login-btn:hover { background: linear-gradient(135deg, #85CE61, #67C23A); }

.divider { display: flex; align-items: center; margin: 20px 0; color: #ccc; font-size: 13px; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: #eee; }
.divider span { padding: 0 16px; }

.login-btn { width: 100%; height: 44px; font-size: 16px; background: #1677FF; border-color: #1677FF; }

.login-footer { text-align: center; font-size: 12px; color: #bbb; margin-top: 24px; }
</style>
