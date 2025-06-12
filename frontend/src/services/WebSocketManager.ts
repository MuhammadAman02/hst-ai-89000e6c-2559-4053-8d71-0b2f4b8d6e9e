import { WorldState, Position, GameStats } from '../types';

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  
  public onWorldUpdate: ((worldState: WorldState) => void) | null = null;
  public onStatsUpdate: ((stats: Partial<GameStats>) => void) | null = null;
  public onConnectionChange: ((connected: boolean) => void) | null = null;

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
          console.log('Connected to game server');
          this.reconnectAttempts = 0;
          if (this.onConnectionChange) {
            this.onConnectionChange(true);
          }
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        this.ws.onclose = () => {
          console.log('Disconnected from game server');
          if (this.onConnectionChange) {
            this.onConnectionChange(false);
          }
          this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            reject(new Error('Connection timeout'));
          }
        }, 5000);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case 'world_update':
        if (this.onWorldUpdate) {
          this.onWorldUpdate(data.worldState);
        }
        break;
      case 'stats_update':
        if (this.onStatsUpdate) {
          this.onStatsUpdate(data.stats);
        }
        break;
      case 'player_joined':
        console.log('Player joined:', data.playerId);
        break;
      case 'player_left':
        console.log('Player left:', data.playerId);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
        });
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.log('Max reconnection attempts reached');
    }
  }

  sendBlockUpdate(position: Position, blockType: number) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'block_update',
        position,
        blockType
      }));
    }
  }

  sendPlayerUpdate(position: Position, rotation: Position) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'player_update',
        position,
        rotation
      }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default WebSocketManager;