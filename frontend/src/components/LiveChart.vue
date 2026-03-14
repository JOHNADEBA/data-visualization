<template>
  <div class="live-chart">
    <div class="chart-header">
      <h3>Real-time Data</h3>
      <select v-model="selectedSource" class="source-select">
        <option value="all">All Sources</option>
        <option v-for="source in availableSources" :key="source" :value="source">
          {{ source.charAt(0).toUpperCase() + source.slice(1) }}
        </option>
      </select>
    </div>
    
    <canvas ref="chartCanvas"></canvas>
    
    <div v-if="hasNoValidData" class="no-data">
      No valid data yet. Start streaming to see charts!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';
import type { DataPoint, DataSource } from '@/types';

Chart.register(...registerables);

const props = defineProps<{
  data: DataPoint[];
  activeSources?: DataSource[];  // Currently selected sources
}>();

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chartInstance: Chart | null = null;

const selectedSource = ref<string>('all');

// Get unique sources from active sources (for dropdown)
const availableSources = computed(() => {
  // Use activeSources if available, otherwise derive from data
  if (props.activeSources && props.activeSources.length > 0) {
    return props.activeSources;
  }
  // Fallback to unique sources from data
  const sources = new Set(props.data.map(d => d.source));
  return Array.from(sources).sort();
});

// Filter data based on selected dropdown AND active sources
const filteredData = computed(() => {
  // First, filter by active sources (unchecked sources are removed)
  let activeFiltered = props.data;
  if (props.activeSources && props.activeSources.length > 0) {
    activeFiltered = props.data.filter(d => 
      props.activeSources!.includes(d.source)
    );
  }
  
  // Then, filter by dropdown selection
  if (selectedSource.value === 'all') {
    return activeFiltered;
  }
  return activeFiltered.filter(d => d.source === selectedSource.value);
});

// Reset dropdown selection if current selection is no longer available
watch(availableSources, (newSources) => {
  if (selectedSource.value !== 'all' && !newSources.includes(selectedSource.value as DataSource)) {
    selectedSource.value = 'all';
  }
});

const hasNoValidData = computed(() => {
  return !filteredData.value.some(d => d.value !== null && d.value !== undefined);
});

// Prepare data for chart
const chartData = computed(() => {
  const points = filteredData.value;
  
  // Group by source for multiple lines
  const sources = new Set(points.map(p => p.source));
  const datasets: any[] = [];
  
  sources.forEach(source => {
    const sourcePoints = points.filter(p => p.source === source);
    
    // Filter out points with null values and map to chart format
    const validPoints = sourcePoints
      .filter(p => p.value !== null && p.value !== undefined)
      .map(p => ({
        x: new Date(p.timestamp),
        y: p.value as number
      }));
    
    // Only create dataset if there are valid points
    if (validPoints.length > 0) {
      datasets.push({
        label: source.charAt(0).toUpperCase() + source.slice(1),
        data: validPoints,
        borderColor: getColorForSource(source),
        backgroundColor: getColorForSource(source, 0.1),
        tension: 0.1,
        pointRadius: 4,
        pointHoverRadius: 6,
        spanGaps: false
      });
    }
  });
  
  return {
    datasets
  };
});

const getColorForSource = (source: string, alpha: number = 1) => {
  const colors: Record<string, string> = {
    weather: `rgba(59, 130, 246, ${alpha})`,     // blue
    stock: `rgba(16, 185, 129, ${alpha})`,      // green
    crypto: `rgba(245, 158, 11, ${alpha})`,     // orange
    mock: `rgba(139, 92, 246, ${alpha})`        // purple
  };
  return colors[source] || `rgba(107, 114, 128, ${alpha})`;
};

// Update chart when data or active sources change
watch([chartData, () => props.activeSources], ([newData, newActiveSources]) => {
  if (chartInstance) {
    chartInstance.data = newData;
    chartInstance.update('none');
  }
}, { deep: true });

// Initialize chart
onMounted(() => {
  if (chartCanvas.value) {
    chartInstance = new Chart(chartCanvas.value, {
      type: 'line',
      data: chartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0
        },
        scales: {
          x: {
            type: 'time',
            adapters: {
              date: {}
            },
            time: {
              displayFormats: {
                second: 'HH:mm:ss',
                minute: 'HH:mm',
                hour: 'HH:00'
              },
              tooltipFormat: 'HH:mm:ss'
            },
            title: {
              display: true,
              text: 'Time'
            }
          },
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: 'Value'
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.dataset.label || '';
                const value = context.parsed.y;
                const dataPoint = props.data[context.dataIndex];
                const unit = dataPoint?.unit || '';
                
                if (value === null || value === undefined || isNaN(value)) {
                  return `${label}: No data`;
                }
                
                return `${label}: ${value.toFixed(2)} ${unit}`;
              }
            }
          }
        }
      }
    });
  }
});

// Clean up chart on component unmount
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<style scoped>
.live-chart {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 400px;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  color: #1f2937;
}

.source-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  font-size: 0.9rem;
  min-width: 120px;
}

canvas {
  flex: 1;
  max-height: 320px;
  width: 100% !important;
}

.no-data {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-style: italic;
}
</style>