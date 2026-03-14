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
              {{ point.source.charAt(0).toUpperCase() + point.source.slice(1) }}
              <span v-if="point.is_mock === false" class="real-data-badge" title="Real data">🔵</span>
              <span v-else-if="point.is_mock === true" class="mock-data-badge" title="Mock data">🟡</span>
            </span>
          </td>
          <td :class="{ 'positive': point.change && point.change > 0, 'negative': point.change && point.change < 0 }">
            {{ point.value?.toFixed(2) ?? 'N/A' }}
          </td>
          <td>{{ point.unit }}</td>
          <td>
            <!-- Weather details -->
            <span v-if="point.source === 'weather'">
              <span v-if="point.location" class="detail-item">📍 {{ point.location }}</span>
              <span v-if="point.conditions" class="detail-item">🌤️ {{ point.conditions }}</span>
              <span v-if="point.humidity" class="detail-item">💧 {{ point.humidity }}%</span>
              <span v-if="point.feels_like" class="detail-item">🤔 Feels {{ point.feels_like }}°</span>
              <span v-if="point.pressure" class="detail-item">📊 {{ point.pressure }} hPa</span>
              <span v-if="!point.location && !point.conditions && !point.humidity" class="detail-item">🌡️ {{
                point.value }}°{{ point.unit }}</span>
            </span>

            <!-- Stock details -->
            <span v-else-if="point.source === 'stock'">
              <span v-if="point.symbol" class="detail-item">🏢 {{ point.symbol }}</span>
              <span v-if="point.change !== undefined" class="detail-item"
                :class="{ 'positive': point.change > 0, 'negative': point.change < 0 }">
                {{ point.change > 0 ? '📈 +' : '📉 ' }}{{ point.change }}%
              </span>
              <span v-if="point.volume" class="detail-item">📊 Vol: {{ formatVolume(point.volume) }}</span>
            </span>

            <!-- Crypto details -->
            <span v-else-if="point.source === 'crypto'">
              <span v-if="point.coin" class="detail-item">₿ {{ point.coin }}</span>
              <span v-if="point.change !== undefined" class="detail-item"
                :class="{ 'positive': point.change > 0, 'negative': point.change < 0 }">
                {{ point.change > 0 ? '📈 +' : '📉 ' }}{{ point.change }}%
              </span>
              <span v-if="point.volume" class="detail-item">📊 Vol: {{ formatVolume(point.volume) }}</span>
            </span>

            <!-- Mock data -->
            <span v-else-if="point.source === 'mock'">
              <span class="detail-item">🎲 Synthetic data</span>
              <span v-if="point.value" class="detail-item">📊 Value: {{ point.value.toFixed(2) }}</span>
            </span>

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

const props = defineProps<{
  data: DataPoint[];
}>();

const reversedData = computed(() => {
  return [...props.data].reverse();
});

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString();
};

const formatVolume = (volume?: number) => {
  if (!volume) return '0';

  if (volume >= 1000000000) {
    return (volume / 1000000000).toFixed(2) + 'B';
  }
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(2) + 'M';
  }
  if (volume >= 1000) {
    return (volume / 1000).toFixed(1) + 'K';
  }
  return volume.toString();
};
</script>

<style scoped>
.data-table {
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  background: white;
}

th {
  text-align: left;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  color: #374151;
  font-weight: 600;
  position: sticky;
  top: 0;
  border-bottom: 2px solid #e5e7eb;
  z-index: 10;
}

td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

tr:hover td {
  background-color: #f9fafb;
}

.source-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
  white-space: nowrap;
}

.source-badge.weather {
  background: #dbeafe;
  color: #1e40af;
}

.source-badge.stock {
  background: #d1fae5;
  color: #065f46;
}

.source-badge.crypto {
  background: #fed7aa;
  color: #92400e;
}

.source-badge.mock {
  background: #e9d5ff;
  color: #6b21a8;
}

.real-data-badge,
.mock-data-badge {
  font-size: 0.7rem;
  margin-left: 0.25rem;
}

.positive {
  color: #059669;
  font-weight: 500;
}

.negative {
  color: #dc2626;
  font-weight: 500;
}

.detail-item {
  display: inline-block;
  margin-right: 0.75rem;
  font-size: 0.8rem;
  color: #4b5563;
}

.detail-item:last-child {
  margin-right: 0;
}

.no-data {
  text-align: center;
  color: #9ca3af;
  padding: 2rem;
  font-style: italic;
}

/* Responsive adjustments */
@media (max-width: 768px) {

  td,
  th {
    padding: 0.5rem;
  }

  .detail-item {
    display: block;
    margin: 0.25rem 0;
  }
}
</style>