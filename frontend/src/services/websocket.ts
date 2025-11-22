/**
 * WebSocket Service for Real-Time Agent Updates
 * Connects to Flask-SocketIO backend
 */

import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:5000';

export interface AgentUpdate {
  agent_id: string;
  agent_name: string;
  status: 'analyzing' | 'processing' | 'complete' | 'error';
  progress: number;
  confidence?: number;
  error?: string;
  patient_id: string;
}

export interface AnalysisComplete {
  analysis_id: string;
  patient_id: string;
  summary: any;
}

export interface ConnectionStatus {
  status: 'connected' | 'disconnected' | 'error';
  timestamp: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(WS_URL, {
          transports: ['websocket', 'polling'],
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionAttempts: 5,
        });

        this.socket.on('connect', () => {
          console.log('✅ WebSocket connected');
          this.emit('connection_status', {
            status: 'connected',
            timestamp: new Date().toISOString(),
          });
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ WebSocket connection error:', error);
          this.emit('connection_status', {
            status: 'error',
            timestamp: new Date().toISOString(),
          });
          reject(error);
        });

        this.socket.on('disconnect', () => {
          console.log('🔌 WebSocket disconnected');
          this.emit('connection_status', {
            status: 'disconnected',
            timestamp: new Date().toISOString(),
          });
        });

        // Listen for agent updates
        this.socket.on('agent_update', (data: AgentUpdate) => {
          console.log('📊 Agent update:', data);
          this.emit('agent_update', data);
        });

        // Listen for analysis completion
        this.socket.on('analysis_complete', (data: AnalysisComplete) => {
          console.log('✅ Analysis complete:', data);
          this.emit('analysis_complete', data);
        });

        // Listen for connection status
        this.socket.on('connection_status', (data: ConnectionStatus) => {
          console.log('🔗 Connection status:', data);
          this.emit('connection_status', data);
        });

        // Listen for subscribed event
        this.socket.on('subscribed', (data: any) => {
          console.log('📢 Subscribed:', data);
          this.emit('subscribed', data);
        });

      } catch (error) {
        console.error('Failed to create socket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.listeners.clear();
    }
  }

  /**
   * Subscribe to patient updates
   */
  subscribe(patientId: string): void {
    if (this.socket && this.socket.connected) {
      this.socket.emit('subscribe', { patient_id: patientId });
    }
  }

  /**
   * Add event listener
   */
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  /**
   * Remove event listener
   */
  off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
    }
  }

  /**
   * Emit event to listeners
   */
  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${event} listener:`, error);
        }
      });
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

// Singleton instance
const wsService = new WebSocketService();

export default wsService;
