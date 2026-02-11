<template>
  <div class="data-preview card">
    <h2 class="card-title">Data Preview</h2>

    <div class="data-info">
      <p><strong>Source:</strong> {{ dataStore.activeSource.name }}</p>
      <p><strong>Total Rows:</strong> {{ dataStore.totalRows.toLocaleString() }}</p>
      <p><strong>Columns:</strong> {{ dataStore.columns.length }}</p>
    </div>

    <div class="table-controls">
      <button @click="toggleExpand">
        {{ expanded ? 'Collapse' : 'Expand' }} Table
      </button>
    </div>

    <div v-if="expanded" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in dataStore.columns" :key="col.name">
              {{ col.name }}
              <span class="col-type">{{ col.dtype }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in dataStore.currentData" :key="index">
            <td v-for="col in dataStore.columns" :key="col.name">
              {{ formatValue(row[col.name]) }}
            </td>
          </tr>
        </tbody>
      </table>

      <div class="table-footer">
        <p>Showing {{ dataStore.currentData.length }} rows</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'

const dataStore = useDataStore()
const expanded = ref(false)

const toggleExpand = () => {
  expanded.value = !expanded.value
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return value.toLocaleString(undefined, { maximumFractionDigits: 4 })
  }
  return value
}
</script>

<style scoped>
.data-preview {
  margin-bottom: 2rem;
}

.data-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.data-info p {
  margin: 0;
}

.table-controls {
  margin-bottom: 1rem;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #eee;
  border-radius: 6px;
  max-height: 500px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: #f8f9fa;
  z-index: 10;
}

.data-table th {
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #eee;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.col-type {
  display: block;
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: normal;
  margin-top: 0.25rem;
}

.table-footer {
  padding: 1rem;
  background: #f8f9fa;
  text-align: center;
  border-top: 1px solid #eee;
}

.table-footer p {
  margin: 0;
  color: #666;
}
</style>
