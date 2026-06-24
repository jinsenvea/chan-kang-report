import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layout/AppLayout.vue'),
    redirect: '/source/list',
    children: [
      { path: 'source/list', name: 'SourceList', component: () => import('@/views/source/list.vue'), meta: { title: '数据源列表' } },
      { path: 'source/push-config', name: 'PushConfig', component: () => import('@/views/source/pushConfig.vue'), meta: { title: '推送规则配置' } },
      { path: 'raw-data', name: 'RawData', component: () => import('@/views/rawData/index.vue'), meta: { title: '原始数据源数据列表' } },
      { path: 'raw-data/:menuCode', name: 'RawDataDynamic', component: () => import('@/views/rawData/DynamicRawData.vue'), meta: { title: '菜单数据' } },
      { path: 'report', name: 'Report', component: () => import('@/views/report/index.vue'), meta: { title: '业务分析数据报表' } },
    ]
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/error/404.vue') }
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, _from, next) => {
  const token = getToken()
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ path: '/source/list' })
  } else {
    next()
  }
})

export default router
