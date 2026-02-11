<template>
  <div class="chart-view card">
    <div class="chart-header">
      <h3>{{ chart.config.title || formatChartType(chart.chart_type) }}</h3>
      <button class="danger" @click="removeChart">Remove</button>
    </div>

    <div class="chart-container" :id="chartId"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Plotly from 'plotly.js-dist-min'
import { useDataStore } from '../stores/dataStore'

const props = defineProps({
  chart: {
    type: Object,
    required: true
  }
})

const dataStore = useDataStore()
const chartId = ref(`chart-${props.chart.chart_id}`)

const renderChart = () => {
  const element = document.getElementById(chartId.value)
  if (element && props.chart.figure) {
    Plotly.newPlot(element, props.chart.figure.data, props.chart.figure.layout, {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      displaylogo: false
    })
  }
}

const removeChart = () => {
  dataStore.removeChart(props.chart.chart_id)
}

const formatChartType = (type) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(() => {
  renderChart()
})

watch(() => props.chart.figure, () => {
  renderChart()
})
</script>

<style scoped>
.chart-view {
  margin-bottom: 2rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  color: #2c3e50;
}

.chart-header button {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.chart-container {
  min-height: 400px;
  width: 100%;
}
</style>
