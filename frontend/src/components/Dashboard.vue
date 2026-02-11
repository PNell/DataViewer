<template>
  <div class="dashboard">
    <!-- Data Source Section -->
    <div class="dashboard-section">
      <FileUpload />
      <DatabaseConnect v-if="showDatabaseConnect" />
    </div>

    <!-- Filters and Data Preview -->
    <div v-if="dataStore.hasActiveSource" class="dashboard-section">
      <FilterPanel />
      <DataPreview />
    </div>

    <!-- Main Content Grid -->
    <div v-if="dataStore.hasActiveSource" class="dashboard-grid">
      <!-- Chart Configuration Sidebar -->
      <aside class="sidebar">
        <ChartConfig />
      </aside>

      <!-- Charts Display Area -->
      <main class="charts-area">
        <div class="charts-header">
          <h2>Charts ({{ dataStore.charts.length }})</h2>
          <button
            v-if="dataStore.charts.length > 0"
            class="secondary"
            @click="dataStore.clearCharts()"
          >
            Clear All Charts
          </button>
        </div>

        <div v-if="dataStore.charts.length === 0" class="no-charts">
          <p>No charts created yet. Use the configuration panel to create your first chart.</p>
        </div>

        <div v-else class="charts-grid">
          <ChartView
            v-for="chart in dataStore.charts"
            :key="chart.chart_id"
            :chart="chart"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'
import FileUpload from './FileUpload.vue'
import DatabaseConnect from './DatabaseConnect.vue'
import DataPreview from './DataPreview.vue'
import FilterPanel from './FilterPanel.vue'
import ChartConfig from './ChartConfig.vue'
import ChartView from './ChartView.vue'

const dataStore = useDataStore()
const showDatabaseConnect = ref(false)
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-section {
  width: 100%;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 2rem;
  align-items: start;
}

.sidebar {
  position: relative;
}

.charts-area {
  min-height: 400px;
}

.charts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.charts-header h2 {
  margin: 0;
  color: #2c3e50;
}

.no-charts {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
  color: #666;
}

.charts-grid {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    top: 0;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
