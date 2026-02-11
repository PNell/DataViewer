<template>
  <div class="filter-builder">
    <h4>Add Filter</h4>

    <!-- Column Selection -->
    <div class="form-group">
      <label>Column</label>
      <select v-model="selectedColumn" @change="onColumnChange">
        <option value="">Select column...</option>
        <optgroup v-if="dataStore.numericColumns.length > 0" label="Numeric">
          <option v-for="col in dataStore.numericColumns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </optgroup>
        <optgroup v-if="dataStore.categoricalColumns.length > 0" label="Categorical">
          <option v-for="col in dataStore.categoricalColumns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </optgroup>
        <optgroup v-if="dataStore.datetimeColumns.length > 0" label="DateTime">
          <option v-for="col in dataStore.datetimeColumns" :key="col.name" :value="col.name">
            {{ col.name }} ({{ col.dtype }})
          </option>
        </optgroup>
      </select>
    </div>

    <!-- Operator Selection -->
    <div class="form-group" v-if="selectedColumn">
      <label>Operator</label>
      <select v-model="selectedOperator" @change="onOperatorChange">
        <option value="">Select operator...</option>
        <option v-for="op in availableOperators" :key="op.value" :value="op.value">
          {{ op.label }}
        </option>
      </select>
    </div>

    <!-- Value Input (Dynamic based on operator) -->
    <div v-if="selectedOperator" class="form-group">
      <label>Value</label>

      <!-- Between operator: two inputs -->
      <div v-if="selectedOperator === 'between'" class="between-inputs">
        <input
          v-model="filterValue"
          :type="valueInputType"
          placeholder="Start value"
          class="value-input"
        />
        <span class="between-separator">and</span>
        <input
          v-model="filterValue2"
          :type="valueInputType"
          placeholder="End value"
          class="value-input"
        />
      </div>

      <!-- In operator: multi-value input -->
      <div v-else-if="selectedOperator === 'in'" class="in-inputs">
        <input
          v-model="filterValueText"
          type="text"
          placeholder="Enter values separated by commas"
          class="value-input"
          @blur="parseInValues"
        />
        <small>Enter multiple values separated by commas</small>
      </div>

      <!-- Equals/Not Equals on categorical: dropdown if available -->
      <div v-else-if="shouldShowDropdown">
        <select v-if="filterOptions.length > 0" v-model="filterValue" class="value-input">
          <option value="">Select value...</option>
          <option v-for="option in filterOptions" :key="option" :value="option">
            {{ option }}
          </option>
        </select>
        <input
          v-else-if="loadingOptions"
          type="text"
          disabled
          placeholder="Loading options..."
          class="value-input"
        />
        <input
          v-else
          v-model="filterValue"
          type="text"
          placeholder="Enter value"
          class="value-input"
        />
      </div>

      <!-- Default: single input -->
      <input
        v-else
        v-model="filterValue"
        :type="valueInputType"
        :placeholder="valuePlaceholder"
        class="value-input"
      />

      <!-- Validation error -->
      <div v-if="validationError" class="validation-error">
        {{ validationError }}
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="form-actions">
      <button @click="applyFilter" :disabled="!canApply" class="btn-primary">
        Apply Filter
      </button>
      <button @click="$emit('cancel')" class="btn-secondary">
        Cancel
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useDataStore } from '../stores/dataStore'

const emit = defineEmits(['add', 'cancel'])

const dataStore = useDataStore()

// Form state
const selectedColumn = ref('')
const selectedOperator = ref('')
const filterValue = ref('')
const filterValue2 = ref('')
const filterValueText = ref('')
const filterOptions = ref([])
const loadingOptions = ref(false)
const validationError = ref('')

// Operator configurations
const OPERATORS = {
  numeric: [
    { value: 'eq', label: 'equals (=)' },
    { value: 'ne', label: 'not equals (≠)' },
    { value: 'gt', label: 'greater than (>)' },
    { value: 'lt', label: 'less than (<)' },
    { value: 'gte', label: 'greater than or equal (≥)' },
    { value: 'lte', label: 'less than or equal (≤)' },
    { value: 'between', label: 'between' }
  ],
  categorical: [
    { value: 'eq', label: 'equals' },
    { value: 'ne', label: 'not equals' },
    { value: 'contains', label: 'contains' },
    { value: 'in', label: 'is one of' }
  ],
  datetime: [
    { value: 'eq', label: 'on date' },
    { value: 'gt', label: 'after' },
    { value: 'lt', label: 'before' },
    { value: 'gte', label: 'on or after' },
    { value: 'lte', label: 'on or before' },
    { value: 'between', label: 'between' }
  ]
}

// Get column data type
const columnDataType = computed(() => {
  if (!selectedColumn.value) return null
  const dataType = dataStore.dataTypes[selectedColumn.value]
  if (dataType === 'numeric') return 'numeric'
  if (dataType === 'datetime' || dataType === 'datetime_candidate') return 'datetime'
  return 'categorical'
})

// Available operators based on column type
const availableOperators = computed(() => {
  if (!columnDataType.value) return []
  return OPERATORS[columnDataType.value] || []
})

// Determine input type
const valueInputType = computed(() => {
  if (columnDataType.value === 'numeric') return 'number'
  if (columnDataType.value === 'datetime') return 'date'
  return 'text'
})

// Value placeholder
const valuePlaceholder = computed(() => {
  if (selectedOperator.value === 'contains') return 'Enter text to search for'
  if (columnDataType.value === 'numeric') return 'Enter number'
  if (columnDataType.value === 'datetime') return 'Select date'
  return 'Enter value'
})

// Should show dropdown for categorical columns with eq/ne operators
const shouldShowDropdown = computed(() => {
  return columnDataType.value === 'categorical' &&
         (selectedOperator.value === 'eq' || selectedOperator.value === 'ne')
})

// Can apply filter validation
const canApply = computed(() => {
  if (!selectedColumn.value || !selectedOperator.value) return false

  if (selectedOperator.value === 'between') {
    return filterValue.value !== '' && filterValue2.value !== '' && !validationError.value
  }

  if (selectedOperator.value === 'in') {
    return filterValue.value !== '' || filterValueText.value !== ''
  }

  return filterValue.value !== ''
})

// Handle column change
const onColumnChange = async () => {
  selectedOperator.value = ''
  filterValue.value = ''
  filterValue2.value = ''
  filterValueText.value = ''
  filterOptions.value = []
  validationError.value = ''

  // Preload filter options for categorical columns
  if (columnDataType.value === 'categorical') {
    await loadFilterOptions()
  }
}

// Handle operator change
const onOperatorChange = () => {
  filterValue.value = ''
  filterValue2.value = ''
  filterValueText.value = ''
  validationError.value = ''

  // Load options when eq/ne selected for categorical
  if (shouldShowDropdown.value && filterOptions.value.length === 0) {
    loadFilterOptions()
  }
}

// Load filter options from API
const loadFilterOptions = async () => {
  if (!selectedColumn.value) return

  loadingOptions.value = true
  try {
    const options = await dataStore.getFilterOptions(selectedColumn.value)
    filterOptions.value = options || []
  } catch (error) {
    console.error('Error loading filter options:', error)
    filterOptions.value = []
  } finally {
    loadingOptions.value = false
  }
}

// Parse comma-separated values for "in" operator
const parseInValues = () => {
  if (filterValueText.value) {
    const values = filterValueText.value.split(',').map(v => v.trim()).filter(v => v)
    filterValue.value = values
  }
}

// Validate between operator
watch([filterValue, filterValue2], () => {
  if (selectedOperator.value === 'between' && filterValue.value && filterValue2.value) {
    const val1 = parseFloat(filterValue.value)
    const val2 = parseFloat(filterValue2.value)

    if (!isNaN(val1) && !isNaN(val2) && val2 <= val1) {
      validationError.value = 'End value must be greater than start value'
    } else {
      validationError.value = ''
    }
  }
})

// Apply filter
const applyFilter = () => {
  if (!canApply.value) return

  const filter = {
    column: selectedColumn.value,
    operator: selectedOperator.value,
    value: filterValue.value
  }

  if (selectedOperator.value === 'between') {
    filter.value2 = filterValue2.value
  }

  // Emit the filter
  emit('add', filter)

  // Reset form
  selectedColumn.value = ''
  selectedOperator.value = ''
  filterValue.value = ''
  filterValue2.value = ''
  filterValueText.value = ''
  validationError.value = ''
}
</script>

<style scoped>
.filter-builder {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
  margin-bottom: 1rem;
}

.filter-builder h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-group select,
.value-input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
  background: white;
}

.form-group select:focus,
.value-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.between-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.between-inputs .value-input {
  flex: 1;
}

.between-separator {
  color: #666;
  font-style: italic;
  padding: 0 0.25rem;
}

.in-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.in-inputs small {
  color: #666;
  font-size: 0.8rem;
}

.validation-error {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.form-actions button {
  flex: 1;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.btn-secondary:active {
  transform: translateY(0);
}
</style>
