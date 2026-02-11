<template>
  <div class="chart-config card">
    <h2 class="card-title">Create Chart</h2>

    <div v-if="!dataStore.hasActiveSource" class="no-data">
      <p>Please upload a CSV file or connect to a database first</p>
    </div>

    <div v-else class="config-form">
      <!-- Chart Type -->
      <div class="form-group">
        <label>Chart Type</label>
        <select v-model="chartType">
          <option value="line">Line Chart</option>
          <option value="bar">Bar Chart</option>
          <option value="scatter">Scatter Plot</option>
          <option value="histogram">Histogram</option>
          <option value="box">Box Plot</option>
          <option value="violin">Violin Plot</option>
          <option value="heatmap">Correlation Heatmap</option>
          <option value="time_series">Time Series</option>
        </select>
      </div>

      <!-- X Axis -->
      <div class="form-group" v-if="showXAxis">
        <label>X Axis</label>
        <select v-model="xColumn">
          <option value="">Select column...</option>
          <option v-for="col in dataStore.columns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </select>
      </div>

      <!-- Y Axis -->
      <div class="form-group" v-if="showYAxis">
        <label>Y Axis</label>
        <select v-model="yColumn">
          <option value="">Select column...</option>
          <option v-for="col in dataStore.numericColumns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </select>
      </div>

      <!-- Color Grouping -->
      <div class="form-group" v-if="showColor">
        <label>Color/Group By (Optional)</label>
        <select v-model="colorColumn">
          <option value="">None</option>
          <option v-for="col in dataStore.categoricalColumns" :key="col.name" :value="col.name">
            {{ col.name }}
          </option>
        </select>
      </div>

      <!-- Chart Title -->
      <div class="form-group">
        <label>Chart Title (Optional)</label>
        <input v-model="chartTitle" type="text" placeholder="Enter chart title">
      </div>

      <!-- Action Buttons -->
      <div class="form-actions">
        <button @click="generateChart" :disabled="!canGenerate || dataStore.loading">
          <span v-if="!dataStore.loading">Generate Chart</span>
          <span v-else>Generating...</span>
        </button>
        <button class="secondary" @click="resetForm">Reset</button>
      </div>

      <div v-if="dataStore.error" class="error">{{ dataStore.error }}</div>
    </div>

    <!-- Chart Suggestions -->
    <div v-if="dataStore.chartSuggestions.length > 0" class="suggestions">
      <h3>Suggested Charts</h3>
      <div class="suggestion-list">
        <div
          v-for="suggestion in dataStore.chartSuggestions.slice(0, 5)"
          :key="suggestion.priority"
          class="suggestion-item"
          @click="applySuggestion(suggestion)"
        >
          <strong>{{ formatChartType(suggestion.chart_type) }}</strong>
          <p>{{ suggestion.reason }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'

const dataStore = useDataStore()

const chartType = ref('line')
const xColumn = ref('')
const yColumn = ref('')
const colorColumn = ref('')
const chartTitle = ref('')

const showXAxis = computed(() => {
  return !['heatmap'].includes(chartType.value)
})

const showYAxis = computed(() => {
  return !['histogram', 'heatmap'].includes(chartType.value)
})

const showColor = computed(() => {
  return !['heatmap'].includes(chartType.value)
})

const canGenerate = computed(() => {
  if (chartType.value === 'heatmap') return true
  if (chartType.value === 'histogram') return xColumn.value !== ''
  return xColumn.value !== '' && yColumn.value !== ''
})

const generateChart = async () => {
  const config = {
    chart_type: chartType.value,
    x_column: xColumn.value || null,
    y_column: yColumn.value || null,
    color_column: colorColumn.value || null,
    title: chartTitle.value || null
  }

  // Special handling for time series
  if (chartType.value === 'time_series' && yColumn.value) {
    config.options = {
      value_columns: [yColumn.value]
    }
  }

  await dataStore.generateChart(config)
}

const resetForm = () => {
  chartType.value = 'line'
  xColumn.value = ''
  yColumn.value = ''
  colorColumn.value = ''
  chartTitle.value = ''
}

const applySuggestion = (suggestion) => {
  chartType.value = suggestion.chart_type
  xColumn.value = suggestion.x_column || ''
  yColumn.value = suggestion.y_column || ''
  chartTitle.value = suggestion.reason
}

const formatChartType = (type) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}
</script>

<style scoped>
.chart-config {
  position: sticky;
  top: 2rem;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.form-actions button {
  flex: 1;
}

.suggestions {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.suggestions h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.suggestion-item strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #667eea;
}

.suggestion-item p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}
</style>
