import { createI18n } from 'vue-i18n'

// 中文语言包
const zh = {
  nav: {
    dashboard: '仪表板',
    analysis: '股票分析',
    config: '配置管理',
    cache: '缓存管理',
    tokens: 'Token统计',
    history: '历史记录',
    status: '系统状态',
    about: '关于'
  },
  dashboard: {
    welcome: '您好，{name}！',
    subtitle: '欢迎使用AI驱动的智能股票分析系统',
    quickActions: '快速操作',
    recentAnalysis: '最近分析',
    marketOverview: '市场概览',
    performance: '系统性能',
    actions: {
      newAnalysis: '新建分析',
      viewReports: '查看报告',
      settings: '系统设置',
      help: '帮助文档'
    },
    stats: {
      totalAnalysis: '总分析次数',
      successRate: '成功率',
      avgTime: '平均用时',
      activeUsers: '活跃用户'
    }
  },
  analysis: {
    title: '股票分析',
    stockCode: '股票代码',
    placeholder: '请输入股票代码，如：000001',
    startAnalysis: '开始分析',
    analyzing: '分析中...',
    result: '分析结果'
  },
  settings: {
    title: '系统设置',
    language: '语言设置',
    theme: '主题设置',
    api: 'API配置',
    save: '保存设置'
  },
  common: {
    testConnection: '测试连接',
    loading: '加载中...',
    success: '成功',
    error: '错误',
    cancel: '取消',
    confirm: '确认'
  }
}

// 英文语言包
const en = {
  nav: {
    dashboard: 'Dashboard',
    analysis: 'Stock Analysis',
    config: 'Configuration',
    cache: 'Cache Management',
    tokens: 'Token Statistics',
    history: 'History Records',
    status: 'System Status',
    about: 'About'
  },
  dashboard: {
    welcome: 'Hello, {name}!',
    subtitle: 'Welcome to AI-powered intelligent stock analysis system',
    quickActions: 'Quick Actions',
    recentAnalysis: 'Recent Analysis',
    marketOverview: 'Market Overview',
    performance: 'System Performance',
    actions: {
      newAnalysis: 'New Analysis',
      viewReports: 'View Reports',
      settings: 'Settings',
      help: 'Help'
    },
    stats: {
      totalAnalysis: 'Total Analysis',
      successRate: 'Success Rate',
      avgTime: 'Avg Time',
      activeUsers: 'Active Users'
    }
  },
  analysis: {
    title: 'Stock Analysis',
    stockCode: 'Stock Code',
    placeholder: 'Enter stock code, e.g.: 000001',
    startAnalysis: 'Start Analysis',
    analyzing: 'Analyzing...',
    result: 'Analysis Result'
  },
  settings: {
    title: 'Settings',
    language: 'Language',
    theme: 'Theme',
    api: 'API Configuration',
    save: 'Save Settings'
  },
  common: {
    testConnection: 'Test Connection',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    cancel: 'Cancel',
    confirm: 'Confirm'
  }
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: 'zh', // 默认语言
  fallbackLocale: 'en',
  globalInjection: true, // 全局注入
  messages: {
    zh,
    en
  }
})

export default i18n
