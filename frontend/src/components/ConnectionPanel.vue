<template>
  <div class="connection-panel" :class="{ connected: status.isConnected }">
    <div class="status-indicator">
      <span class="dot" :class="{ connected: status.isConnected }"></span>
      <span>{{ status.isConnected ? 'Connected' : 'Disconnected' }}</span>
    </div>

    <div v-if="!status.isConnected" class="connection-form">
      <input v-model="clientId" placeholder="Enter client ID (optional)" class="input" />
      <button @click="handleConnect" class="btn primary" :disabled="isConnecting">
        {{ isConnecting ? 'Connecting...' : 'Connect' }}
      </button>
    </div>

    <div v-else class="connection-info">
      <span class="client-id">ID: {{ status.clientId }}</span>
      <button @click="handleDisconnect" class="btn secondary">Disconnect</button>
    </div>

    <div v-if="status.error" class="error-message">
      ⚠️ {{ status.error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { ConnectionStatus } from '@/types';

// Define props with proper TypeScript type
const props = defineProps<{
  status: ConnectionStatus;
}>();

const emit = defineEmits<{
  (e: 'connect', clientId?: string): void;
  (e: 'disconnect'): void;
}>();

const clientId = ref('');
const isConnecting = ref(false);

const handleConnect = async () => {
  isConnecting.value = true;
  try {
    await emit('connect', clientId.value || undefined);
  } finally {
    isConnecting.value = false;
  }
};

const handleDisconnect = () => {
  emit('disconnect');
};
</script>

<style scoped>
.connection-panel {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.connection-panel.connected {
  border-left: 4px solid #10b981;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ef4444;
}

.dot.connected {
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }

  70% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.connection-form {
  display: flex;
  gap: 0.5rem;
}

.input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn.primary {
  background: #3b82f6;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn.secondary {
  background: #6b7280;
  color: white;
}

.btn.secondary:hover {
  background: #4b5563;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.connection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.client-id {
  font-family: monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.error-message {
  margin-top: 0.5rem;
  color: #ef4444;
  font-size: 0.9rem;
  padding: 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
}
</style>