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

      <!-- Y Axis (single select for non-line charts) -->
      <div class="form-group" v-if="showYAxis && !showMultiYSelector">
        <label>Y Axis</label>
        <select v-model="yColumn">
          <option value="">Select column...</option>
          <option v-for="col in dataStore.numericColumns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </select>
      </div>

      <!-- Y Axis Columns (multi-select for line charts) -->
      <div class="form-group" v-if="showMultiYSelector">
        <label>Y Axis Columns</label>
        <div class="multi-select-container">
          <div v-for="col in dataStore.numericColumns" :key="col.name" class="checkbox-row">
            <label class="checkbox-label">
              <input type="checkbox" :value="col.name" v-model="yColumns" />
              <span>{{ col.name }} ({{ col.dtype }})</span>
            </label>
            <label
              v-if="yColumns.includes(col.name) && yColumns.length >= 2"
              class="secondary-axis-toggle"
              title="Assign to right-side Y axis"
            >
              <input type="checkbox" :value="col.name" v-model="secondaryYColumns" />
              <span class="axis-badge">Y2</span>
            </label>
          </div>
        </div>
        <p v-if="yColumns.length >= 2" class="help-text">
          Check Y2 to assign a column to the secondary (right) axis
        </p>
      </div>

      <!-- Color Grouping -->
      <div class="form-group" v-if="showColor">
        <label>{{ chartType === 'scatter' ? 'Color By (Optional)' : 'Color/Group By (Optional)' }}</label>
        <select v-model="colorColumn">
          <option value="">None</option>
          <optgroup v-if="chartType === 'scatter'" label="Categorical">
            <option v-for="col in dataStore.categoricalColumns" :key="'cat-' + col.name" :value="col.name">
              {{ col.name }}
            </option>
          </optgroup>
          <optgroup v-if="chartType === 'scatter'" label="Numeric (gradient)">
            <option v-for="col in dataStore.numericColumns" :key="'num-' + col.name" :value="'numeric:' + col.name">
              {{ col.name }} (continuous)
            </option>
          </optgroup>
          <template v-if="chartType !== 'scatter'">
            <option v-for="col in dataStore.categoricalColumns" :key="col.name" :value="col.name">
              {{ col.name }}
            </option>
          </template>
        </select>
      </div>

      <!-- ==================== Chart-Specific Options ==================== -->

      <!-- Bar Chart Options -->
      <div class="options-section" v-if="showBarOptions">
        <label class="section-label">Bar Chart Options</label>
        <div class="form-group">
          <label>Bar Mode</label>
          <select v-model="barMode">
            <option value="group">Grouped</option>
            <option value="stack">Stacked</option>
          </select>
        </div>
        <div class="form-group">
          <label>Sort Order</label>
          <select v-model="sortOrder">
            <option value="">None</option>
            <option value="asc">Ascending (by value)</option>
            <option value="desc">Descending (by value)</option>
            <option value="alpha">Alphabetical (by label)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Orientation</label>
          <select v-model="orientation">
            <option value="v">Vertical</option>
            <option value="h">Horizontal</option>
          </select>
        </div>
      </div>

      <!-- Scatter Plot Options -->
      <div class="options-section" v-if="showScatterOptions">
        <label class="section-label">Scatter Options</label>
        <div class="form-group">
          <label>Size Column (Optional)</label>
          <select v-model="sizeColumn">
            <option value="">None</option>
            <option v-for="col in dataStore.numericColumns" :key="col.name" :value="col.name">
              {{ col.name }}
            </option>
          </select>
        </div>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showTrendline" />
            <span>Show Trendline</span>
          </label>
        </div>
        <div class="form-group" v-if="showTrendline">
          <label>Trendline Type</label>
          <select v-model="trendlineDegree">
            <option :value="1">Linear</option>
            <option :value="2">Quadratic</option>
            <option :value="3">Cubic</option>
          </select>
        </div>
      </div>

      <!-- Histogram Options -->
      <div class="options-section" v-if="showHistogramOptions">
        <label class="section-label">Distribution Analysis</label>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showDistributionFit" />
            <span>Show Normal Distribution Fit</span>
          </label>
        </div>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showStatistics" />
            <span>Show Statistics</span>
          </label>
        </div>
      </div>

      <!-- Box/Violin Options -->
      <div class="options-section" v-if="showBoxViolinOptions">
        <label class="section-label">{{ chartType === 'box' ? 'Box Plot' : 'Violin Plot' }} Options</label>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showPoints" />
            <span>Show Individual Data Points</span>
          </label>
        </div>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="horizontalOrientation" />
            <span>Horizontal Orientation</span>
          </label>
        </div>
      </div>

      <!-- Heatmap Options -->
      <div class="options-section" v-if="showHeatmapOptions">
        <label class="section-label">Heatmap Options</label>
        <div class="form-group">
          <label>Color Scale</label>
          <select v-model="heatmapColorscale">
            <option value="RdBu">Red-Blue (RdBu)</option>
            <option value="Viridis">Viridis</option>
            <option value="Plasma">Plasma</option>
            <option value="Inferno">Inferno</option>
            <option value="YlOrRd">Yellow-Orange-Red</option>
            <option value="Blues">Blues</option>
          </select>
        </div>
        <div class="checkbox-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showHeatmapAnnotations" />
            <span>Show Value Annotations</span>
          </label>
        </div>
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
import { ref, computed, watch } from 'vue'
import { useDataStore } from '../stores/dataStore'

const dataStore = useDataStore()

// Core chart config
const chartType = ref('line')
const xColumn = ref('')
const yColumn = ref('')
const colorColumn = ref('')
const chartTitle = ref('')

// Line chart: multi-Y + secondary axis
const yColumns = ref([])
const secondaryYColumns = ref([])

// Bar chart options
const barMode = ref('group')
const sortOrder = ref('')
const orientation = ref('v')

// Scatter options
const showTrendline = ref(false)
const trendlineDegree = ref(1)
const sizeColumn = ref('')

// Histogram options
const showDistributionFit = ref(false)
const showStatistics = ref(false)

// Box/Violin options
const showPoints = ref(false)
const horizontalOrientation = ref(false)

// Heatmap options
const heatmapColorscale = ref('RdBu')
const showHeatmapAnnotations = ref(true)

// Computed visibility flags
const showXAxis = computed(() => {
  return !['heatmap'].includes(chartType.value)
})

const showYAxis = computed(() => {
  return !['histogram', 'heatmap'].includes(chartType.value)
})

const showColor = computed(() => {
  return !['heatmap'].includes(chartType.value)
})

const showMultiYSelector = computed(() => {
  return chartType.value === 'line'
})

const showBarOptions = computed(() => {
  return chartType.value === 'bar'
})

const showScatterOptions = computed(() => {
  return chartType.value === 'scatter'
})

const showHistogramOptions = computed(() => {
  return chartType.value === 'histogram'
})

const showBoxViolinOptions = computed(() => {
  return ['box', 'violin'].includes(chartType.value)
})

const showHeatmapOptions = computed(() => {
  return chartType.value === 'heatmap'
})

const canGenerate = computed(() => {
  if (chartType.value === 'heatmap') return true
  if (chartType.value === 'histogram') return xColumn.value !== ''
  if (chartType.value === 'line') {
    return xColumn.value !== '' && (yColumn.value !== '' || yColumns.value.length > 0)
  }
  return xColumn.value !== '' && yColumn.value !== ''
})

// Watchers
watch(yColumns, (newVal) => {
  secondaryYColumns.value = secondaryYColumns.value.filter(c => newVal.includes(c))
})

watch(chartType, () => {
  // Reset chart-specific options when switching types
  yColumns.value = []
  secondaryYColumns.value = []
  barMode.value = 'group'
  sortOrder.value = ''
  orientation.value = 'v'
  showTrendline.value = false
  trendlineDegree.value = 1
  sizeColumn.value = ''
  showDistributionFit.value = false
  showStatistics.value = false
  showPoints.value = false
  horizontalOrientation.value = false
  heatmapColorscale.value = 'RdBu'
  showHeatmapAnnotations.value = true
})

const generateChart = async () => {
  const config = {
    chart_type: chartType.value,
    x_column: xColumn.value || null,
    y_column: yColumn.value || null,
    color_column: null,
    title: chartTitle.value || null,
    options: {}
  }

  // Handle color column — detect numeric color for scatter
  if (colorColumn.value) {
    if (colorColumn.value.startsWith('numeric:')) {
      config.options.color_numeric = colorColumn.value.replace('numeric:', '')
    } else {
      config.color_column = colorColumn.value
    }
  }

  // Line chart: multi-Y columns
  if (chartType.value === 'line' && yColumns.value.length > 0) {
    config.options.y_columns = [...yColumns.value]
    config.y_column = yColumns.value[0]
    if (secondaryYColumns.value.length > 0) {
      config.options.secondary_y_columns = [...secondaryYColumns.value]
    }
  }

  // Bar chart options
  if (chartType.value === 'bar') {
    if (barMode.value !== 'group') {
      config.options.bar_mode = barMode.value
    }
    if (sortOrder.value) {
      config.options.sort_order = sortOrder.value
    }
    if (orientation.value !== 'v') {
      config.options.orientation = orientation.value
    }
  }

  // Scatter options
  if (chartType.value === 'scatter') {
    if (sizeColumn.value) {
      config.size_column = sizeColumn.value
    }
    if (showTrendline.value) {
      config.options.show_trendline = true
      config.options.trendline_degree = trendlineDegree.value
    }
  }

  // Time series handling
  if (chartType.value === 'time_series' && yColumn.value) {
    config.options = {
      ...config.options,
      value_columns: [yColumn.value]
    }
  }

  // Histogram options
  if (chartType.value === 'histogram') {
    if (showDistributionFit.value) {
      config.options.show_distribution_fit = true
    }
    if (showStatistics.value) {
      config.options.show_statistics = true
    }
  }

  // Box/Violin options
  if (['box', 'violin'].includes(chartType.value)) {
    if (showPoints.value) {
      config.options.show_points = true
    }
    if (horizontalOrientation.value) {
      config.options.horizontal = true
    }
  }

  // Heatmap options
  if (chartType.value === 'heatmap') {
    if (heatmapColorscale.value !== 'RdBu') {
      config.options.colorscale = heatmapColorscale.value
    }
    if (!showHeatmapAnnotations.value) {
      config.options.show_annotations = false
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
  yColumns.value = []
  secondaryYColumns.value = []
  barMode.value = 'group'
  sortOrder.value = ''
  orientation.value = 'v'
  showTrendline.value = false
  trendlineDegree.value = 1
  sizeColumn.value = ''
  showDistributionFit.value = false
  showStatistics.value = false
  showPoints.value = false
  horizontalOrientation.value = false
  heatmapColorscale.value = 'RdBu'
  showHeatmapAnnotations.value = true
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

/* Options sections */
.options-section {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.options-section .form-group {
  gap: 0.35rem;
}

.section-label {
  font-weight: 700;
  color: #667eea;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Multi-select for Y columns */
.multi-select-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 0.5rem;
}

.checkbox-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.35rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

.secondary-axis-toggle {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  font-size: 0.8rem;
}

.axis-badge {
  background: #667eea;
  color: white;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.help-text {
  font-size: 0.8rem;
  color: #888;
  margin: 0.25rem 0 0 0;
}

/* Suggestions */
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
