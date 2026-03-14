<template>
    <div class="parameter-form">
        <h3>Data Stream Parameters</h3>

        <form @submit.prevent="handleSubmit">
            <div class="form-group">
                <label>Data Sources:</label>
                <div class="checkbox-group">
                    <label v-for="source in availableSources" :key="source" class="checkbox-label">
                        <input type="checkbox" :value="source" :checked="isSelected(source)"
                            @change="toggleSource(source)" />
                        {{ source.charAt(0).toUpperCase() + source.slice(1) }}
                    </label>
                </div>
                <div class="selected-sources-hint" v-if="selectedSources.length > 0">
                    Selected: {{ selectedSources.join(', ') }}
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Interval (seconds):</label>
                    <input type="number" v-model.number="formData.interval" min="0.5" step="0.5" class="input" />
                </div>
            </div>

            <!-- Conditional fields based on selected sources -->
            <div v-if="selectedSources.includes('weather')" class="conditional-fields">
                <h4>Weather Settings</h4>
                <div class="form-group">
                    <label>City:</label>
                    <input type="text" v-model="formData.city" placeholder="e.g., London" class="input" />
                </div>
            </div>

            <div v-if="selectedSources.includes('stock')" class="conditional-fields">
                <h4>Stock Settings</h4>
                <div class="form-group">
                    <label>Symbol:</label>
                    <input type="text" v-model="formData.symbol" placeholder="e.g., AAPL" class="input" />
                </div>
            </div>

            <div v-if="selectedSources.includes('crypto')" class="conditional-fields">
                <h4>Crypto Settings</h4>
                <div class="form-group">
                    <label>Coin:</label>
                    <input type="text" v-model="formData.coin" placeholder="e.g., bitcoin" class="input" />
                </div>
            </div>

            <div class="button-group">
                <button v-if="!isStreaming" type="submit" class="btn primary"
                    :disabled="!canSubmit || !props.isConnected">
                    Start Streaming
                </button>

                <button v-if="isStreaming" type="button" class="btn secondary" @click="stopStreaming">
                    Stop Streaming
                </button>
            </div>

            <p v-if="!props.isConnected" class="hint">
                ⚠️ Connect to WebSocket first
            </p>

            <p v-if="isStreaming" class="streaming-hint">
                ⚡ Live streaming - check/uncheck sources to update in real-time
            </p>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { DataSource } from '@/types';

const props = defineProps<{
    isConnected: boolean;
    isStreaming: boolean;
}>();

const emit = defineEmits<{
    (e: 'submit', params: any): void;
    (e: 'stop'): void;
    (e: 'update', params: any): void;
}>();

const availableSources: DataSource[] = ['weather', 'stock', 'crypto', 'mock'];

// Use a simple array for selected sources
const selectedSources = ref<DataSource[]>(['mock']);

// Form data object
const formData = ref({
    interval: 2,
    city: 'London',
    symbol: 'AAPL',
    coin: 'bitcoin'
});

// Check if a source is selected
const isSelected = (source: DataSource): boolean => {
    return selectedSources.value.includes(source);
};

// Toggle source on/off
const toggleSource = (source: DataSource) => {
    let newSources: DataSource[];

    if (selectedSources.value.includes(source)) {
        // Removing a source
        if (props.isStreaming && selectedSources.value.length === 1) {
            // Prevent removing the last source while streaming
            alert('Cannot remove all sources while streaming. Stop the stream first or keep at least one source.');
            return;
        }
        newSources = selectedSources.value.filter(s => s !== source);
    } else {
        // Adding a source
        newSources = [...selectedSources.value, source];
    }

    selectedSources.value = newSources;

    // If streaming, send update immediately
    if (props.isStreaming) {
        emit('update', {
            sources: selectedSources.value
        });
    }
};

// Watch for interval changes
watch(() => formData.value.interval, (newInterval) => {
    if (props.isStreaming) {
        emit('update', { interval: newInterval });
    }
});

// Watch for conditional field changes
watch(() => formData.value.city, (newCity) => {
    if (props.isStreaming && selectedSources.value.includes('weather')) {
        emit('update', { city: newCity });
    }
});

watch(() => formData.value.symbol, (newSymbol) => {
    if (props.isStreaming && selectedSources.value.includes('stock')) {
        emit('update', { symbol: newSymbol });
    }
});

watch(() => formData.value.coin, (newCoin) => {
    if (props.isStreaming && selectedSources.value.includes('crypto')) {
        emit('update', { coin: newCoin });
    }
});

const canSubmit = computed(() => selectedSources.value.length > 0);

const handleSubmit = () => {
    if (canSubmit.value && props.isConnected && !props.isStreaming) {
        const paramsToSend = {
            sources: selectedSources.value,
            interval: formData.value.interval,
            city: formData.value.city,
            symbol: formData.value.symbol,
            coin: formData.value.coin
        };

        emit('submit', paramsToSend);
    }
};

const stopStreaming = () => {
    emit('stop');
};
</script>

<style scoped>
.parameter-form {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h3 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #1f2937;
}

.form-group {
    margin-bottom: 1rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #4b5563;
}

.input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: border-color 0.2s;
}

.input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.checkbox-group {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: normal;
    cursor: pointer;
    margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
    margin: 0;
}

.selected-sources-hint {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.5rem;
    padding: 0.25rem 0.5rem;
    background: #f3f4f6;
    border-radius: 4px;
    display: inline-block;
}

.conditional-fields {
    margin: 1rem 0;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 4px;
    border-left: 3px solid #3b82f6;
}

.conditional-fields h4 {
    margin-top: 0;
    margin-bottom: 1rem;
    color: #374151;
    font-size: 0.95rem;
}

.button-group {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.btn {
    flex: 1;
    padding: 0.75rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    font-size: 1rem;
    transition: all 0.2s;
}

.btn.primary {
    background: #3b82f6;
    color: white;
}

.btn.primary:hover:not(:disabled) {
    background: #2563eb;
}

.btn.primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn.secondary {
    background: #6b7280;
    color: white;
}

.btn.secondary:hover {
    background: #4b5563;
}

.hint {
    text-align: center;
    color: #ef4444;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.streaming-hint {
    text-align: center;
    color: #10b981;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    font-weight: 500;
}
</style>