// src/api/client.ts - Backend API client
const API_BASE_URL = 'http://localhost:5000';

// Types matching backend responses
export interface ChannelStatus {
  on: boolean;
  fault: boolean;
  over_current: boolean;
  over_temp: boolean;
}

export interface Channel {
  id: number;
  name: string;
  voltage: number;
  current: number;
  temperature: number;
  status: ChannelStatus;
}

export interface SystemStatus {
  timestamp: string;
  system_voltage: number;
  total_current: number;
  channels: Channel[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface TestScenario {
  name: string;
  description: string;
  elapsed: number;
  status: 'idle' | 'active' | 'complete';
  current_event: string;
}

// API Client
export class PdmApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Health check
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  }

  // Get system status (complete PDM data)
  async getStatus(): Promise<SystemStatus> {
    const response = await fetch(`${this.baseUrl}/api/pdm/status`);
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
  }

  // Get all channels
  async getChannels(): Promise<Channel[]> {
    const response = await fetch(`${this.baseUrl}/api/pdm/channels`);
    if (!response.ok) throw new Error('Failed to get channels');
    const data = await response.json();
    return data.channels;
  }

  // Get specific channel
  async getChannel(channelId: number): Promise<Channel> {
    const response = await fetch(`${this.baseUrl}/api/pdm/channel/${channelId}`);
    if (!response.ok) throw new Error('Failed to get channel');
    const data = await response.json();
    return data.channel;
  }

  // Get system voltage and current
  async getSystemInfo(): Promise<{
    system_voltage: number;
    total_current: number;
    active_channels: number;
  }> {
    const response = await fetch(`${this.baseUrl}/api/pdm/system`);
    if (!response.ok) throw new Error('Failed to get system info');
    return response.json();
  }

  // Note: Control endpoints not implemented in Python backend yet
  // These are placeholders for future implementation
  async controlChannel(channelId: number, enabled: boolean): Promise<{ status: string; channel: number; enabled: boolean; in_use?: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/pdm/channel/${channelId}/set`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    if (!response.ok) throw new Error('Failed to set channel state');
    return response.json();
  }

  async emergencyShutdown(): Promise<string> {
    console.warn('Emergency shutdown not implemented in Python backend yet');
    return 'Emergency shutdown not available';
  }

  async resetAll(): Promise<string> {
    console.warn('Reset not implemented in Python backend yet');
    return 'Reset not available';
  }

  // Test scenario controls
  async triggerScenario(scenarioId: number): Promise<{ status: string; scenario_id: number }> {
    const response = await fetch(`${this.baseUrl}/api/pdm/trigger-scenario`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
    if (!response.ok) throw new Error('Failed to trigger scenario');
    return response.json();
  }

  async getTestScenario(): Promise<TestScenario> {
    const response = await fetch(`${this.baseUrl}/api/pdm/test-scenario`);
    if (!response.ok) throw new Error('Failed to get test scenario');
    return response.json();
  }
}

// Export singleton instance
export const pdmApi = new PdmApiClient();
