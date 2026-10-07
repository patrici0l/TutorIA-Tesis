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
}
