/**
 * API client for DataViewer backend
 */
import axios from 'axios'

const API_BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // CSV Upload
  async uploadCSV(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Database Connection
  async connectDatabase(config) {
    const response = await apiClient.post('/database/connect', config)
    return response.data
  },

  async getTableSchema(tableName, config) {
    const response = await apiClient.post(`/database/tables/${tableName}`, config)
    return response.data
  },

  // Data Operations
  async queryData(sourceId, filters = [], limit = 100, offset = 0, columns = null) {
    const response = await apiClient.post('/data/query', {
      source_id: sourceId,
      filters,
      limit,
      offset,
      columns
    })
    return response.data
  },

  async getColumns(sourceId) {
    const response = await apiClient.get(`/data/columns/${sourceId}`)
    return response.data
  },

  async getSummaryStats(sourceId) {
    const response = await apiClient.get(`/data/summary/${sourceId}`)
    return response.data
  },

  async getFilterOptions(sourceId, column, limit = 100) {
    const response = await apiClient.post('/data/filter-options', null, {
      params: { source_id: sourceId, column, limit }
    })
    return response.data
  },

  // Chart Generation
  async generateChart(chartConfig) {
    const response = await apiClient.post('/charts/generate', chartConfig)
    return response.data
  },

  async generateChartsBatch(chartConfigs) {
    const response = await apiClient.post('/charts/batch', chartConfigs)
    return response.data
  },

  // Analysis
  async getChartSuggestions(sourceId, maxSuggestions = 10) {
    const response = await apiClient.get(`/analysis/suggestions/${sourceId}`, {
      params: { max_suggestions: maxSuggestions }
    })
    return response.data
  },

  async detectOutliers(sourceId, column, method = 'iqr', threshold = 1.5) {
    const response = await apiClient.post('/analysis/outliers', {
      source_id: sourceId,
      column,
      method,
      threshold
    })
    return response.data
  },

  async getCorrelation(sourceId) {
    const response = await apiClient.get(`/analysis/correlation/${sourceId}`)
    return response.data
  }
}
