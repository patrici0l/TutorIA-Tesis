import { SearchHit } from '../../rag/modelos/search.model';

export type ResourceType = 'EXPLANATION' | 'EXERCISE' | 'QUIZ' | 'FEEDBACK';
export type Difficulty = 'basic' | 'intermediate' | 'advanced';
export interface PreparationRequest {
  topic: string;
  learning_objective: string;
  resource_type: ResourceType;
  difficulty: Difficulty;
  question_count?: number;
  student_answer?: string;
}
export interface PreparationResponse {
  id: string;
  status: 'prepared';
  topic: string;
  learning_objective: string;
  resource_type: ResourceType;
  difficulty: Difficulty;
  question_count: number | null;
  sources: (SearchHit & { citation_id: string })[];
}
