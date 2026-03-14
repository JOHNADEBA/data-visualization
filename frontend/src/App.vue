<template>
  <div id="app">
    <Dashboard />
  </div>
</template>

<script setup lang="ts">
import Dashboard from './views/Dashboard.vue'
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f3f4f6;
  color: #1f2937;
  line-height: 1.5;
}

#app {
  min-height: 100vh;
}
</style>