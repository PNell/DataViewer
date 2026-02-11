/**
 * Pinia store for data and chart state management
 */
import { defineStore } from 'pinia'
import api from '../services/api'

export const useDataStore = defineStore('data', {
  state: () => ({
    // Data Source
    activeSource: null, // { source_id, source_type, name, columns }
    currentData: [],
    totalRows: 0,

    // Columns and Types
    columns: [],
    dataTypes: {},

    // Filters
    activeFilters: [],

    // Charts
    charts: [], // Array of { chart_id, chart_type, figure, config }

    // UI State
    loading: false,
    error: null,

    // Suggestions
    chartSuggestions: []
  }),

  getters: {
    numericColumns: (state) => {
      return state.columns.filter(col =>
        state.dataTypes[col.name] === 'numeric'
      )
    },

    categoricalColumns: (state) => {
      return state.columns.filter(col =>
        state.dataTypes[col.name] === 'categorical'
      )
    },

    datetimeColumns: (state) => {
      return state.columns.filter(col =>
        state.dataTypes[col.name] === 'datetime' ||
        state.dataTypes[col.name] === 'datetime_candidate'
      )
    },

    hasActiveSource: (state) => {
      return state.activeSource !== null
    }
  },

  actions: {
    // Upload CSV
    async uploadCSV(file) {
      this.loading = true
      this.error = null
      try {
        const response = await api.uploadCSV(file)
        this.activeSource = {
          source_id: response.source_id,
          source_type: 'csv',
          name: response.filename
        }
        this.columns = response.columns
        this.currentData = response.preview
        this.totalRows = response.rows

        // Get data types
        await this.fetchDataTypes()

        // Get chart suggestions
        await this.fetchChartSuggestions()

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // Connect to SQL Server
    async connectDatabase(config) {
      this.loading = true
      this.error = null
      try {
        const response = await api.connectDatabase(config)
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async selectTable(tableName, config) {
      this.loading = true
      this.error = null
      try {
        const response = await api.getTableSchema(tableName, config)
        this.activeSource = {
          source_id: response.source_id,
          source_type: 'sql_server',
          name: response.table_name
        }
        this.columns = response.columns
        this.totalRows = response.row_count || 0

        // Load preview data
        await this.queryData()

        // Get data types
        await this.fetchDataTypes()

        // Get chart suggestions
        await this.fetchChartSuggestions()

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // Query data
    async queryData(limit = 100, offset = 0, columns = null) {
      if (!this.activeSource) {
        throw new Error('No active data source')
      }

      this.loading = true
      this.error = null
      try {
        const response = await api.queryData(
          this.activeSource.source_id,
          this.activeFilters,
          limit,
          offset,
          columns
        )
        this.currentData = response.data
        this.totalRows = response.total_rows
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // Fetch data types
    async fetchDataTypes() {
      if (!this.activeSource) return

      try {
        const response = await api.getColumns(this.activeSource.source_id)
        this.dataTypes = response.data_types
      } catch (error) {
        console.error('Error fetching data types:', error)
      }
    },

    // Add filter
    addFilter(filter) {
      this.activeFilters.push(filter)
      this.queryData()
    },

    // Remove filter
    removeFilter(index) {
      this.activeFilters.splice(index, 1)
      this.queryData()
    },

    // Clear filters
    clearFilters() {
      this.activeFilters = []
      this.queryData()
    },

    // Generate chart
    async generateChart(chartConfig) {
      if (!this.activeSource) {
        throw new Error('No active data source')
      }

      this.loading = true
      this.error = null
      try {
        const config = {
          source_id: this.activeSource.source_id,
          ...chartConfig,
          filters: this.activeFilters
        }

        const response = await api.generateChart(config)

        // Add to charts array
        this.charts.push({
          chart_id: response.chart_id,
          chart_type: response.chart_type,
          figure: response.figure,
          config: chartConfig
        })

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // Remove chart
    removeChart(chartId) {
      const index = this.charts.findIndex(c => c.chart_id === chartId)
      if (index !== -1) {
        this.charts.splice(index, 1)
      }
    },

    // Clear all charts
    clearCharts() {
      this.charts = []
    },

    // Fetch chart suggestions
    async fetchChartSuggestions() {
      if (!this.activeSource) return

      try {
        const response = await api.getChartSuggestions(this.activeSource.source_id)
        this.chartSuggestions = response.suggestions
      } catch (error) {
        console.error('Error fetching chart suggestions:', error)
      }
    },

    // Get summary statistics
    async getSummaryStats() {
      if (!this.activeSource) {
        throw new Error('No active data source')
      }

      try {
        const response = await api.getSummaryStats(this.activeSource.source_id)
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    // Reset state
    reset() {
      this.activeSource = null
      this.currentData = []
      this.totalRows = 0
      this.columns = []
      this.dataTypes = {}
      this.activeFilters = []
      this.charts = []
      this.chartSuggestions = []
      this.error = null
    }
  }
})
