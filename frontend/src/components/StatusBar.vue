<template>
  <div class="data-table">
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Source</th>
          <th>Value</th>
          <th>Unit</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(point, index) in reversedData" :key="index">
          <td>{{ formatTime(point.timestamp) }}</td>
          <td>
            <span class="source-badge" :class="point.source">
              {{ point.source }}
            </span>
          </td>
          <td>{{ point.value?.toFixed(2) ?? 'N/A' }}</td>
          <td>{{ point.unit }}</td>
          <td>
            <span v-if="point.location">{{ point.location }}</span>
            <span v-else-if="point.symbol">{{ point.symbol }}</span>
            <span v-else-if="point.coin">{{ point.coin }}</span>
            <span v-else>—</span>
          </td>
        </tr>
        <tr v-if="props.data.length === 0">
          <td colspan="5" class="no-data">No data points yet</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DataPoint } from '@/types';

// Define props with proper TypeScript type
const props = defineProps<{
  data: DataPoint[];
}>();

const reversedData = computed(() => {
  return [...props.data].reverse();
});

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString();
};
</script>

<style scoped>
.status-bar {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.status-header h3 {
    margin: 0;
    color: #1f2937;
}

.clear-btn {
    padding: 0.25rem 0.75rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.clear-btn:hover:not(:disabled) {
    background: #e5e7eb;
}

.clear-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.messages-container {
    max-height: 200px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.85rem;
    background: #1f2937;
    color: #e5e7eb;
    border-radius: 4px;
    padding: 1rem;
}

.message {
    margin-bottom: 0.5rem;
    line-height: 1.4;
    word-wrap: break-word;
}

.message:last-child {
    margin-bottom: 0;
}

.time {
    color: #9ca3af;
    margin-right: 0.5rem;
}

.content {
    color: #e5e7eb;
}

.message.data .content {
    color: #10b981;
}

.message.error .content {
    color: #ef4444;
}

.message.system .content {
    color: #60a5fa;
}

.message.complete .content {
    color: #f59e0b;
}

.no-messages {
    color: #6b7280;
    text-align: center;
    padding: 1rem;
}
</style>