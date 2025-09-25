// This file exports application ports/interfaces as they are added
// For now, this is a placeholder to maintain Clean Architecture structure

// Base port interface that all application ports should extend
export interface BasePort {
  readonly id: string;
}

// Placeholder exports to make this a proper TypeScript module
export const APPLICATION_PORTS = {
  version: '1.0.0',
  type: 'application-ports'
} as const;

export type ApplicationPortsType = typeof APPLICATION_PORTS;