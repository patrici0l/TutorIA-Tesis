export interface HealthResponse {
  status: 'ok' | 'degraded';
  api: 'ok';
  database: 'ok' | 'unavailable';
  pgvector: 'ok' | 'unavailable';
  version: string;
}

export function isHealthResponse(value: unknown): value is HealthResponse {
  if (!value || typeof value !== 'object') return false;
  const data = value as Record<string, unknown>;
  return (
    ['ok', 'degraded'].includes(String(data['status'])) &&
    data['api'] === 'ok' &&
    ['ok', 'unavailable'].includes(String(data['database'])) &&
    ['ok', 'unavailable'].includes(String(data['pgvector'])) &&
    typeof data['version'] === 'string'
  );
}
