export interface KnownTokenSum {
  known_sum: number | null;
  known_records: number;
  unknown_records: number;
}
export interface MetricsSummary {
  scope: 'own_all_time';
  observed_at: string;
  total_records: number;
  prepared: number;
  generating: number;
  succeeded: number;
  failed: number;
  reserved_attempts: number;
  execution_records: number;
  input_tokens: KnownTokenSum;
  output_tokens: KnownTokenSum;
  total_tokens: KnownTokenSum;
  latency: {
    known_average_ms: string | null;
    known_min_ms: number | null;
    known_max_ms: number | null;
    known_records: number;
    unknown_records: number;
  };
  cost_known_records: number;
  cost_unknown_records: number;
}
