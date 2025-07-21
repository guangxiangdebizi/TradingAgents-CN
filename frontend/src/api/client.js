/**
 * API 客户端 - 与后端微服务通信
 */

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * HTTP 请求封装
 */
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
  }

  /**
   * 发送 HTTP 请求
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`)
      
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      console.log(`✅ API Response: ${config.method || 'GET'} ${url}`, data)
      
      return data
    } catch (error) {
      console.error(`❌ API Error: ${config.method || 'GET'} ${url}`, error)
      throw error
    }
  }

  /**
   * GET 请求
   */
  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    
    return this.request(url, {
      method: 'GET'
    })
  }

  /**
   * POST 请求
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  /**
   * PUT 请求
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  /**
   * DELETE 请求
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    })
  }
}

// 创建全局 API 客户端实例
const apiClient = new ApiClient()

/**
 * 分析相关 API
 */
export const analysisApi = {
  /**
   * 开始股票分析
   */
  async startAnalysis(analysisRequest) {
    return apiClient.post('/api/analysis/start', analysisRequest)
  },

  /**
   * 获取分析进度
   */
  async getProgress(analysisId) {
    return apiClient.get(`/api/analysis/${analysisId}/progress`)
  },

  /**
   * 获取分析结果
   */
  async getResult(analysisId) {
    return apiClient.get(`/api/analysis/${analysisId}/result`)
  },

  /**
   * 取消分析任务
   */
  async cancelAnalysis(analysisId) {
    return apiClient.delete(`/api/analysis/${analysisId}`)
  }
}

/**
 * 数据相关 API
 */
export const dataApi = {
  /**
   * 获取股票基本信息
   */
  async getStockInfo(symbol) {
    return apiClient.get(`/api/stock/info/${symbol}`)
  },

  /**
   * 获取股票历史数据
   */
  async getStockData(stockDataRequest) {
    return apiClient.post('/api/stock/data', stockDataRequest)
  },

  /**
   * 获取股票基本面数据
   */
  async getStockFundamentals(symbol, startDate, endDate, currDate) {
    return apiClient.get(`/api/stock/fundamentals/${symbol}`, {
      start_date: startDate,
      end_date: endDate,
      curr_date: currDate
    })
  },

  /**
   * 获取股票新闻
   */
  async getStockNews(symbol) {
    return apiClient.get(`/api/stock/news/${symbol}`)
  }
}

/**
 * 配置相关 API
 */
export const configApi = {
  /**
   * 获取模型配置
   */
  async getModelConfig() {
    return apiClient.get('/api/config/models')
  },

  /**
   * 获取系统状态
   */
  async getSystemStatus() {
    return apiClient.get('/api/config/status')
  }
}

/**
 * 健康检查 API
 */
export const healthApi = {
  /**
   * 检查系统健康状态
   */
  async checkHealth() {
    return apiClient.get('/health')
  }
}

/**
 * 导出相关 API
 */
export const exportApi = {
  /**
   * 导出分析报告
   */
  async exportReport(analysisId, format) {
    const response = await fetch(`${API_BASE_URL}/api/export/${format}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        analysis_id: analysisId,
        format: format
      })
    })

    if (!response.ok) {
      throw new Error(`导出失败: ${response.statusText}`)
    }

    // 处理文件下载
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis_${analysisId}_${Date.now()}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    return { success: true, message: '导出成功' }
  }
}

// 默认导出 API 客户端
export default apiClient
