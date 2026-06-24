import axios, { AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken, isDemoMode } from './auth'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

request.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      removeToken()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (!error.response) {
      ElMessage.warning('后端服务未连接，当前为静态预览模式')
    } else {
      const msg = error.response?.data?.detail || error.message || '请求失败'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

/* ============================================================
   演示模式 — 模拟数据
   ============================================================ */
const MOCK: Record<string, () => any> = {
  'post /api/auth/login': () => ({
    token: 'demo-token-2026',
    username: 'demo',
    realName: '演示账号',
  }),

  'get /api/source/list': () => ({
    data: [
      { id: 1, source_name: 'K3Cloud 生产环境', base_url: 'https://k3cloud.example.com', account: 'admin', client_type: 'K3Cloud', login_api: '/api/login', data_api: '/api/data/list', page_size: 100, enable: true },
      { id: 2, source_name: '金蝶云星辰', base_url: 'https://star.example.com', account: 'demo_user', client_type: '金蝶云', login_api: '/auth/login', data_api: '/data/query', page_size: 50, enable: true },
      { id: 3, source_name: '本地测试环境', base_url: 'http://localhost:8080', account: 'test', client_type: 'K3Cloud', login_api: '/api/login', data_api: '/api/data/list', page_size: 200, enable: false },
    ]
  }),
  'post /api/source/create': () => ({ ok: true, msg: '新增成功' }),
  'put /api/source/update': () => ({ ok: true, msg: '更新成功' }),
  'post /api/source/test-connect': () => ({ ok: true, msg: '连接成功 ✓' }),

  'get /api/menu/list': () => ({
    data: [
      { id: 1, menu_code: 'order_detail', menu_name: '营业明细', list_api: '/api/order/list', export_api: '/api/order/export', source_id: 1 },
      { id: 2, menu_code: 'product_sales', menu_name: '产品销售统计', list_api: '/api/product/sales', export_api: '/api/product/export', source_id: 1 },
      { id: 3, menu_code: 'customer_analysis', menu_name: '客户分析', list_api: '/api/customer/analysis', export_api: '/api/customer/export', source_id: 2 },
    ]
  }),
  'post /api/menu/create': () => ({ ok: true, msg: '菜单已新增' }),
  'put /api/menu/update': () => ({ ok: true, msg: '菜单已更新' }),
  'delete /api/menu/delete': () => ({ ok: true, msg: '菜单已删除' }),
  'get /api/menu/detail': () => ({
    menu_code: 'order_detail', menu_name: '营业明细',
    list_api: '/api/order/list', export_api: '/api/order/export',
    filter_schema: '[{"field":"store_id","label":"门店","type":"select","options":[{"label":"总店","value":"store_001"},{"label":"分店A","value":"store_002"}]}]',
  }),

  'get /api/report/list': () => ({
    data: [
      { id: 1, report_name: '月度营业报表', source_id: 1, crawl_params: '{"menu_code":"order_detail"}', cron_expr: '0 8 1 * *', auto_push: true, task_status: 'idle', last_crawl_at: '2026-06-24 08:00:00' },
      { id: 2, report_name: '产品销售周报', source_id: 1, crawl_params: '{"menu_code":"product_sales"}', cron_expr: '0 9 * * 1', auto_push: true, task_status: 'running', last_crawl_at: '2026-06-23 09:00:00' },
      { id: 3, report_name: '客户分析月报', source_id: 2, crawl_params: '{"menu_code":"customer_analysis"}', cron_expr: '0 10 1 * *', auto_push: false, task_status: 'idle', last_crawl_at: '2026-06-01 10:00:00' },
    ]
  }),
  'post /api/report/create': () => ({ ok: true, msg: '报表任务已创建' }),
  'post /api/report/re-crawl': () => ({ run_id: 'run_' + Date.now(), msg: '开始爬取' }),
  'get /api/report/task-progress': () => ({
    progress: 100, status: 'completed', msg: '爬取完成',
    logs: ['[10:00:00] 开始爬取', '[10:00:05] 请求第 1 页，获取 50 条', '[10:00:08] 请求第 2 页，获取 50 条', '[10:00:10] 爬取完成，共 100 条'],
  }),
  'post /api/report/cron-config': () => ({ ok: true, msg: '定时配置已更新' }),
  'post /api/report/push': () => ({ ok: true, msg: '推送成功' }),

  'get /api/raw-data/list': () => ({
    data: Array.from({ length: 15 }, (_, i) => ({
      id: i + 1, source_id: 1, menu_code: 'order_detail',
      raw_json: JSON.stringify({ order_no: 'ORD' + String(20260001 + i).padStart(8, '0'), amount: Math.round(Math.random() * 5000 * 100) / 100, store: i % 2 === 0 ? '总店' : '分店A' }),
      fetch_time: '2026-06-' + String(20 + (i % 10)).padStart(2, '0') + ' 08:00:00',
    }))
  }),
  'get /api/raw-data/export': () => ({ url: '/chan-kang-report/demo_export.xlsx' }),

  'get /api/push-config/list': () => ({
    data: [
      { id: 1, name: '钉钉-运营群', source_id: 1, channel: 'dingtalk', webhook: 'https://oapi.dingtalk.com/robot/send?access_token=demo', enable: true },
      { id: 2, name: '飞书-技术群', source_id: 1, channel: 'feishu', webhook: 'https://open.feishu.cn/open-apis/bot/v2/hook/demo', enable: true },
      { id: 3, name: '企业微信-日报', source_id: 2, channel: 'wecom', webhook: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=demo', enable: false },
    ]
  }),
  'post /api/push-config/create': () => ({ ok: true, msg: '推送规则已创建' }),
  'put /api/push-config/update': () => ({ ok: true, msg: '推送规则已更新' }),
  'post /api/push-config/test-push': () => ({ ok: true, msg: '测试消息已发送，请查看群聊' }),
}

function matchMock(method: string, url: string): (() => any) | null {
  const path = url.split('?')[0]
  for (const [key, handler] of Object.entries(MOCK)) {
    const [m, pattern] = key.split(' ')
    if (m.toLowerCase() !== method.toLowerCase()) continue
    if (path === pattern || path.startsWith(pattern + '/')) return handler
  }
  return null
}

/**
 * 演示模式适配器 — 替换 axios 默认适配器
 * 匹配到模拟数据则直接返回，否则走真实请求
 */
const demoAdapter: typeof request.defaults.adapter = (config) => {
  if (isDemoMode()) {
    const handler = matchMock(config.method || 'get', config.url || '')
    if (handler) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({ data: handler(), status: 200, statusText: 'OK', headers: {}, config })
        }, 200) // 加一点延迟模拟真实请求
      })
    }
  }
  // 真实请求
  const realAdapter = axios.defaults.adapter!
  return realAdapter(config)
}

request.defaults.adapter = demoAdapter

export default request
