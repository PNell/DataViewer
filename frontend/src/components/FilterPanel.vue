<template>
  <div class="filter-panel card">
    <!-- Filter Header -->
    <div class="filter-header">
      <div class="filter-title">
        <h3>Filters</h3>
        <span v-if="activeFilterCount > 0" class="filter-badge">
          {{ activeFilterCount }}
        </span>
      </div>
      <div class="filter-actions">
        <button
          v-if="!showFilterBuilder"
          @click="showFilterBuilder = true"
          class="btn-add"
          title="Add new filter"
        >
          + Add Filter
        </button>
        <button
          v-if="activeFilterCount > 0"
          @click="handleClearAll"
          class="btn-clear"
          title="Clear all filters"
        >
          Clear All
        </button>
        <button @click="toggleExpand" class="btn-toggle" :title="isExpanded ? 'Collapse' : 'Expand'">
          {{ isExpanded ? '−' : '+' }}
        </button>
      </div>
    </div>

    <!-- Filter Content (Collapsible) -->
    <transition name="expand">
      <div v-if="isExpanded" class="filter-content">
        <!-- Filter Builder -->
        <FilterBuilder
          v-if="showFilterBuilder"
          @add="handleAddFilter"
          @cancel="showFilterBuilder = false"
        />

        <!-- Active Filters List -->
        <div v-if="activeFilterCount > 0 && !showFilterBuilder" class="active-filters">
          <div class="active-filters-header">
            <span>Active Filters:</span>
          </div>
          <div class="active-filters-list">
            <ActiveFilter
              v-for="(filter, index) in dataStore.activeFilters"
              :key="index"
              :filter="filter"
              :index="index"
              @remove="handleRemoveFilter"
            />
          </div>
        </div>

        <!-- No Filters Message -->
        <div v-if="activeFilterCount === 0 && !showFilterBuilder" class="no-filters">
          <p>No filters applied. Click "Add Filter" to filter your data.</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'
import FilterBuilder from './FilterBuilder.vue'
import ActiveFilter from './ActiveFilter.vue'

const dataStore = useDataStore()

// Component state
const isExpanded = ref(true)
const showFilterBuilder = ref(false)

// Computed properties
const activeFilterCount = computed(() => {
  return dataStore.activeFilters.length
})

// Methods
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const handleAddFilter = (filter) => {
  dataStore.addFilter(filter)
  showFilterBuilder.value = false
}

const handleRemoveFilter = (index) => {
  dataStore.removeFilter(index)
}

const handleClearAll = () => {
  if (activeFilterCount.value > 3) {
    // Confirmation for many filters
    if (!confirm(`Are you sure you want to clear all ${activeFilterCount.value} filters?`)) {
      return
    }
  }
  dataStore.clearFilters()
}
</script>

<style scoped>
.filter-panel {
  margin-bottom: 1.5rem;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-title h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  height: 1.5rem;
  padding: 0 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-actions button {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-add:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-clear {
  background: #6c757d;
  color: white;
}

.btn-clear:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-toggle {
  background: #e9ecef;
  color: #495057;
  font-size: 1.2rem;
  width: 2rem;
  height: 2rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.btn-toggle:hover {
  background: #dee2e6;
}

.filter-content {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.active-filters {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.active-filters-header {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.active-filters-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.no-filters {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 6px;
}

.no-filters p {
  margin: 0;
}

/* Expand/Collapse Animation */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 1000px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .filter-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .active-filters-list {
    flex-direction: column;
  }
}
</style>
