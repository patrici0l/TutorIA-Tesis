import {
  PreparationResponse,
  EducationalResource,
  ResourceType,
  Difficulty,
} from './preparation.model';

export type GenerationStatus = 'prepared' | 'generating' | 'succeeded' | 'failed';
export interface HistoryItem {
  id: string;
  topic: string;
  resource_type: ResourceType;
  difficulty: Difficulty;
  status: GenerationStatus;
  created_at: string;
  completed_at: string | null;
}
export interface HistoryPage {
  items: HistoryItem[];
  total: number;
  offset: number;
  limit: number;
}
export interface HistoryDetail {
  preparation: PreparationResponse;
  status: GenerationStatus;
  created_at: string;
  completed_at: string | null;
  resource: EducationalResource | null;
  message: string | null;
  audit?: GenerationAudit | null;
}

export interface GenerationAudit {
  generation_started_at: string | null;
  provider: string | null;
  requested_model: string | null;
  model_version: string | null;
  prompt_version: string;
  prompt_sha256: string;
  usage: {
    input_tokens: number | null;
    output_tokens: number | null;
    total_tokens: number | null;
    reasoning_tokens: number | null;
    cached_input_tokens: number | null;
  } | null;
  latency_ms: number | null;
  estimated_cost: string | null;
  cost_basis?: {
    version: 'confirmed-free-tier-v1';
    currency: 'USD';
    basis: 'operator_confirmed_free_tier';
    provider: 'gemini';
    requested_model: string;
    input_per_million: '0';
    output_per_million: '0';
  } | null;
  error_code: string | null;
  retrieval: {
    method: 'exact_cosine';
    query_version: string;
    embedding_model: string;
    embedding_revision: string;
    embedding_version: string;
    top_k: number;
    min_similarity: number;
    available_chunks: number;
    elapsed_ms: number;
  };
}
