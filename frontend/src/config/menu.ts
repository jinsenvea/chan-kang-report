export interface MenuItem {
  id: number
  name: string
  path: string
  icon?: string
  children?: MenuItem[]
  dynamic?: boolean  // 动态菜单标记
}

export const menuList: MenuItem[] = [
  {
    id: 1,
    name: '爬取数据源配置',
    path: '_source',
    icon: 'DataLine',
    children: [
      { id: 101, name: '数据源列表', path: '/source/list' },
      { id: 102, name: '推送规则配置', path: '/source/push-config' }
    ]
  },
  {
    id: 2,
    name: '原始数据源数据列表',
    path: '/raw-data',
    icon: 'Document',
    children: []  // 留空，启动时从后端动态加载菜单
  },
  { id: 3, name: '业务分析数据报表', path: '/report', icon: 'DataAnalysis' }
]
