// Data source types
export type DataSource = "weather" | "stock" | "crypto" | "mock";

export interface StreamParameters {
  sources: DataSource[];
  interval: number; // seconds
  max_points: number;
  // Source-specific parameters
  city?: string; // for weather
  symbol?: string; // for stocks
  coin?: string; // for crypto
}

export interface DataPoint {
  source: DataSource;
  value: number | null;
  unit: string;
  timestamp: string;

  // Real vs mock indicator
  is_mock?: boolean;

  // Weather fields
  location?: string;
  conditions?: string;
  humidity?: number;
  feels_like?: number;
  pressure?: number;

  // Stock fields
  symbol?: string;
  change?: number;
  volume?: number;

  // Crypto fields
  coin?: string;

  // Tracking fields
  point_number?: number;
  total_points?: number;
}

export interface WebSocketMessage {
  type:
    | "system"
    | "data"
    | "error"
    | "status"
    | "batch_complete"
    | "complete"
    | "stream_started";
  message?: string;
  timestamp: string;
  // For data messages
  point_number?: number;
  total_points?: number;
  data?: DataPoint;
  // For stream_started
  params?: StreamParameters;
}

export interface ConnectionStatus {
  isConnected: boolean;
  clientId: string | null;
  error: string | null;
}
