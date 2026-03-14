import { ref, onUnmounted } from "vue";
import type { Ref } from "vue";
import type {
  WebSocketMessage,
  StreamParameters,
  ConnectionStatus,
  DataPoint,
} from "@/types";

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null);
  const status = ref<ConnectionStatus>({
    isConnected: false,
    clientId: null,
    error: null,
  });

  const messages: Ref<WebSocketMessage[]> = ref([]);
  const latestData: Ref<DataPoint[]> = ref([]);

  // Generate a random client ID
  const generateClientId = (): string => {
    return "client_" + Math.random().toString(36).substring(2, 10);
  };

  // Connect to WebSocket
  const connect = (clientId: string = generateClientId()): Promise<void> => {
    return new Promise((resolve, reject) => {
      // Use environment variable or fallback to localhost
      const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000";
      
      const socket = new WebSocket(`${wsUrl}/ws/${clientId}`);

      socket.onopen = () => {
        status.value = {
          isConnected: true,
          clientId,
          error: null,
        };
        ws.value = socket;
        resolve();
      };

      socket.onerror = (error) => {
        status.value.error = "WebSocket connection error";
        reject(error);
      };

      socket.onclose = () => {
        status.value.isConnected = false;
        status.value.clientId = null;
        ws.value = null;
      };

      socket.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          messages.value.push(data);

          // Keep messages array manageable
          if (messages.value.length > 100) {
            messages.value = messages.value.slice(-100);
          }

          // If it's data, add to latest data for charts
          if (data.type === "data" && data.data) {
            latestData.value.push({
              ...data.data,
              point_number: data.point_number,
              total_points: data.total_points,
              timestamp: data.timestamp,
            });

            // Keep only last 50 points for chart
            if (latestData.value.length > 50) {
              latestData.value = latestData.value.slice(-50);
            }
          }
        } catch (e) {
          console.error("Failed to parse message:", e);
        }
      };
    });
  };

  // Send stream parameters
  const startStreaming = (params: StreamParameters) => {
    if (ws.value && status.value.isConnected) {
      ws.value.send(JSON.stringify(params));
    } else {
      throw new Error("Not connected");
    }
  };

  // Send update message during active stream
  const sendUpdate = (updateMessage: any) => {
    if (ws.value && status.value.isConnected) {
      ws.value.send(
        JSON.stringify({
          type: "UPDATE_STREAM",
          ...updateMessage,
        }),
      );
    } else {
      console.error("Cannot send update - not connected");
    }
  };

  // Disconnect
  const disconnect = () => {
    if (ws.value) {
      ws.value.close();
    }
  };

  // Clear messages
  const clearMessages = () => {
    messages.value = [];
    latestData.value = [];
  };

  // Auto-disconnect on component unmount
  onUnmounted(() => {
    disconnect();
  });

  return {
    ws,
    status,
    messages,
    latestData,
    connect,
    disconnect,
    startStreaming,
    sendUpdate,
    clearMessages,
  };
}
