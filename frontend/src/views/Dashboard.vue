<template>
    <div class="dashboard">
        <header class="dashboard-header">
            <h1>Real-Time Data Visualization</h1>
            <p>Stream live data from multiple sources with WebSocket</p>
        </header>

        <div class="dashboard-grid">
            <div class="controls-section">
                <ConnectionPanel :status="ws.status.value" @connect="handleConnect" @disconnect="handleDisconnect" />
                <ParameterForm :is-connected="ws.status.value.isConnected" :is-streaming="isStreaming"
                    @submit="handleStreamStart" @update="handleStreamUpdate" @stop="handleStreamStop" />
            </div>

            <div class="visualization-section">
                <LiveChart :data="ws.latestData.value" :active-sources="activeSources" />

                <div class="data-table-container">
                    <h3>Recent Data Points</h3>
                    <DataTable :data="ws.latestData.value" />
                </div>
            </div>
        </div>

        <div class="status-section">
            <div class="message-log">
                <h3>Message Log</h3>
                <button @click="ws.clearMessages" class="clear-btn">Clear</button>
                <div class="messages-container" ref="messagesContainer">
                    <div v-for="(msg, index) in ws.messages.value" :key="index" class="message" :class="msg.type">
                        <span class="time">[{{ formatTime(msg.timestamp) }}]</span>
                        <span class="content">
                            <strong v-if="msg.type === 'data'">📊 Data #{{ msg.point_number }}:</strong>
                            <strong v-else-if="msg.type === 'error'">❌ Error:</strong>
                            <strong v-else-if="msg.type === 'system'">🔧 System:</strong>
                            <strong v-else-if="msg.type === 'complete'">✅ Complete:</strong>
                            <strong v-else>ℹ️ Info:</strong>

                            <template v-if="msg.type === 'data' && msg.data">
                                {{ msg.data.source }}: {{ msg.data.value?.toFixed(2) }} {{ msg.data.unit }}
                            </template>
                            <template v-else>
                                {{ msg.message }}
                            </template>
                        </span>
                    </div>

                    <div v-if="ws.messages.value.length === 0" class="no-messages">
                        No messages yet. Connect and start streaming!
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue';
import { useWebSocket } from '@/composables/useWebSocket';
import ConnectionPanel from '@/components/ConnectionPanel.vue';
import ParameterForm from '@/components/ParameterForm.vue';
import LiveChart from '@/components/LiveChart.vue';
import DataTable from '@/components/DataTable.vue';
import type { StreamParameters, DataSource } from '@/types';

const ws = useWebSocket();
const messagesContainer = ref<HTMLElement | null>(null);
const isStreaming = ref(false);
const activeSources = ref<DataSource[]>(['mock']);  // Track active sources

const handleConnect = async (clientId?: string) => {
    try {
        await ws.connect(clientId);
    } catch (error) {
        console.error('Connection failed:', error);
    }
};

const handleDisconnect = () => {
    ws.disconnect();
    isStreaming.value = false;
};

const handleStreamStart = (params: StreamParameters) => {
    isStreaming.value = true;
    activeSources.value = params.sources;  // Store active sources
    ws.startStreaming(params);
};

const handleStreamUpdate = (updateMessage: any) => {
    // Update active sources if sources changed
    if (updateMessage.sources) {
        activeSources.value = updateMessage.sources;
    }

    ws.sendUpdate(updateMessage);
};

const handleStreamStop = () => {
    isStreaming.value = false;
    ws.disconnect();
    setTimeout(() => {
        ws.connect();
    }, 100);
};

const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
};

// WATCH 1: Auto-scroll to bottom when new messages arrive
watch(() => ws.messages.value.length, async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
});

// WATCH 2: Watch for stream completion (though now continuous, this may not trigger)
watch(() => ws.messages.value, (messages) => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.type === 'complete') {
        isStreaming.value = false;
    }
}, { deep: true });

// Optional: Watch for WebSocket disconnection
watch(() => ws.status.value.isConnected, (isConnected) => {
    if (!isConnected) {
        isStreaming.value = false;
    }
});
</script>


<style scoped>
.dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.dashboard-header {
    margin-bottom: 2rem;
}

.dashboard-header h1 {
    margin: 0;
    color: #1f2937;
    font-size: 2rem;
}

.dashboard-header p {
    margin: 0.5rem 0 0;
    color: #6b7280;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.controls-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.visualization-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.data-table-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data-table-container h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    color: #1f2937;
}

.status-section {
    margin-top: 1.5rem;
}

.message-log {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-log h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    color: #1f2937;
}

.clear-btn {
    padding: 0.25rem 0.75rem;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.clear-btn:hover {
    background: #e5e7eb;
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

@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .dashboard {
        padding: 1rem;
    }
}
</style>