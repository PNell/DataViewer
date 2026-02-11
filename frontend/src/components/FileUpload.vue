<template>
  <div class="file-upload card">
    <h2 class="card-title">Upload CSV File</h2>

    <div
      class="drop-zone"
      :class="{ 'drag-over': isDragging }"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
    >
      <div v-if="!uploading" class="drop-zone-content">
        <svg class="upload-icon" viewBox="0 0 24 24" width="48" height="48">
          <path fill="currentColor" d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13,9V3.5L18.5,9H13Z" />
        </svg>
        <p class="drop-text">Drag and drop CSV file here</p>
        <p class="drop-text-or">or</p>
        <label for="file-input" class="file-label">
          <button type="button" @click="$refs.fileInput.click()">
            Choose File
          </button>
        </label>
        <input
          ref="fileInput"
          id="file-input"
          type="file"
          accept=".csv"
          @change="handleFileSelect"
          style="display: none"
        />
      </div>

      <div v-else class="uploading">
        <div class="spinner"></div>
        <p>Uploading and processing file...</p>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="uploadedFile" class="file-info">
      <h3>Uploaded: {{ uploadedFile }}</h3>
      <p>{{ totalRows }} rows loaded</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDataStore } from '../stores/dataStore'

const dataStore = useDataStore()

const isDragging = ref(false)
const uploading = ref(false)
const error = ref(null)
const uploadedFile = ref(null)
const totalRows = ref(0)

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadFile(file)
  }
}

const handleDrop = async (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]

  if (file && file.name.endsWith('.csv')) {
    await uploadFile(file)
  } else {
    error.value = 'Please upload a CSV file'
  }
}

const uploadFile = async (file) => {
  uploading.value = true
  error.value = null

  try {
    const response = await dataStore.uploadCSV(file)
    uploadedFile.value = file.name
    totalRows.value = response.rows
  } catch (err) {
    error.value = err.message || 'Error uploading file'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-upload {
  margin-bottom: 2rem;
}

.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  transition: all 0.3s ease;
  background: #fafafa;
}

.drop-zone.drag-over {
  border-color: #667eea;
  background: #f0f2ff;
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  color: #667eea;
}

.drop-text {
  font-size: 1.1rem;
  color: #666;
}

.drop-text-or {
  font-size: 0.9rem;
  color: #999;
}

.file-label button {
  margin-top: 0.5rem;
}

.uploading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.file-info {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #e7f3ff;
  border-radius: 6px;
}

.file-info h3 {
  color: #1976d2;
  margin-bottom: 0.5rem;
}
</style>
