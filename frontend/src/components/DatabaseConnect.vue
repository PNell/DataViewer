<template>
  <div class="database-connect card">
    <h2 class="card-title">Connect to SQL Server</h2>

    <div class="connection-form">
      <div class="form-group">
        <label>Server</label>
        <input v-model="config.server" type="text" placeholder="localhost or server IP">
      </div>

      <div class="form-group">
        <label>Database</label>
        <input v-model="config.database" type="text" placeholder="Database name">
      </div>

      <div class="form-group">
        <label>
          <input type="checkbox" v-model="config.use_windows_auth">
          Use Windows Authentication
        </label>
      </div>

      <div v-if="!config.use_windows_auth">
        <div class="form-group">
          <label>Username</label>
          <input v-model="config.username" type="text" placeholder="SQL Server username">
        </div>

        <div class="form-group">
          <label>Password</label>
          <input v-model="config.password" type="password" placeholder="Password">
        </div>
      </div>

      <div class="form-actions">
        <button @click="connect" :disabled="connecting || !canConnect">
          {{ connecting ? 'Connecting...' : 'Connect' }}
        </button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <!-- Table Selection -->
      <div v-if="tables.length > 0" class="table-selection">
        <h3>Select Table</h3>
        <select v-model="selectedTable" @change="loadTable">
          <option value="">Choose a table...</option>
          <option v-for="table in tables" :key="table" :value="table">
            {{ table }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDataStore } from '../stores/dataStore'

const dataStore = useDataStore()

const config = ref({
  server: '',
  database: '',
  username: '',
  password: '',
  use_windows_auth: false,
  port: 1433
})

const connecting = ref(false)
const error = ref(null)
const tables = ref([])
const selectedTable = ref('')

const canConnect = computed(() => {
  if (!config.value.server || !config.value.database) return false
  if (!config.value.use_windows_auth) {
    return config.value.username && config.value.password
  }
  return true
})

const connect = async () => {
  connecting.value = true
  error.value = null

  try {
    const response = await dataStore.connectDatabase(config.value)
    tables.value = response.tables
  } catch (err) {
    error.value = err.message || 'Connection failed'
  } finally {
    connecting.value = false
  }
}

const loadTable = async () => {
  if (!selectedTable.value) return

  try {
    await dataStore.selectTable(selectedTable.value, config.value)
  } catch (err) {
    error.value = err.message || 'Error loading table'
  }
}
</script>

<style scoped>
.database-connect {
  margin-bottom: 2rem;
}

.connection-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.form-group label input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.form-actions {
  margin-top: 1rem;
}

.table-selection {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.table-selection h3 {
  margin-bottom: 1rem;
}
</style>
