<template>
  <div id="app">
    <header class="app-header">
      <h1>DataViewer</h1>
      <p>Dynamic Data Visualization & EDA Platform</p>
    </header>

    <main class="app-main">
      <Dashboard />
    </main>
  </div>
</template>

<script setup>
import Dashboard from './components/Dashboard.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.app-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Global Button Styles */
button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  background: #667eea;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

button.secondary {
  background: #6c757d;
}

button.secondary:hover {
  background: #5a6268;
}

button.danger {
  background: #dc3545;
}

button.danger:hover {
  background: #c82333;
}

/* Global Input Styles */
input, select, textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  width: 100%;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Card Styles */
.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Loading Spinner */
.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Message */
.error {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}
</style>
