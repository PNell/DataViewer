<template>
  <div class="active-filter-tag" :class="`type-${filterType}`">
    <span class="filter-column">{{ filter.column }}</span>
    <span class="filter-operator">{{ operatorLabel }}</span>
    <span class="filter-value">{{ valueDisplay }}</span>
    <button @click="$emit('remove', index)" class="btn-remove" title="Remove filter">
      ×
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDataStore } from '../stores/dataStore'

const props = defineProps({
  filter: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})

defineEmits(['remove'])

const dataStore = useDataStore()

// Determine filter type based on column data type
const filterType = computed(() => {
  const dataType = dataStore.dataTypes[props.filter.column]
  if (!dataType) return 'categorical'

  if (dataType === 'numeric') return 'numeric'
  if (dataType === 'datetime' || dataType === 'datetime_candidate') return 'datetime'
  return 'categorical'
})

// Operator labels mapping
const OPERATOR_LABELS = {
  eq: '=',
  ne: '≠',
  gt: '>',
  lt: '<',
  gte: '≥',
  lte: '≤',
  contains: 'contains',
  in: 'in',
  between: 'between'
}

const operatorLabel = computed(() => {
  return OPERATOR_LABELS[props.filter.operator] || props.filter.operator
})

// Format value display
const valueDisplay = computed(() => {
  const { value, value2, operator } = props.filter

  if (operator === 'between' && value2 !== undefined) {
    return `${value} and ${value2}`
  }

  if (operator === 'in' && Array.isArray(value)) {
    return value.join(', ')
  }

  return value
})
</script>

<style scoped>
.active-filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  background: #e9ecef;
  margin: 0.25rem;
  transition: all 0.2s ease;
}

.active-filter-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Type-based color coding */
.type-numeric {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.type-categorical {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.type-datetime {
  background: #e7d4f5;
  color: #6c2d91;
  border: 1px solid #d8bfed;
}

.filter-column {
  font-weight: 600;
}

.filter-operator {
  color: #666;
  font-style: italic;
  font-size: 0.85rem;
  padding: 0 0.25rem;
}

.filter-value {
  font-family: 'Courier New', monospace;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.btn-remove {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.25rem;
  font-weight: bold;
  cursor: pointer;
  padding: 0 0.25rem;
  line-height: 1;
  transition: all 0.2s ease;
}

.btn-remove:hover {
  color: #c82333;
  transform: scale(1.2);
}

.btn-remove:active {
  transform: scale(1);
}
</style>
