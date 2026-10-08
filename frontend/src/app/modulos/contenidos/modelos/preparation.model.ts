import { SearchHit } from '../../rag/modelos/search.model';
import { ProfileResponse } from '../../perfiles/modelos/profile.model';

export type ResourceType = 'EXPLANATION' | 'EXERCISE' | 'QUIZ' | 'FEEDBACK';
export type Difficulty = 'basic' | 'intermediate' | 'advanced';
export interface PreparationRequest {
  topic: string;
  learning_objective: string;
  resource_type: ResourceType;
  difficulty: Difficulty;
  question_count?: number;
  student_answer?: string;
  profile_id?: string;
}
export interface AdaptationSnapshot {
  policy_version: string;
  profile: ProfileResponse;
  requested_difficulty: Difficulty;
  effective_difficulty: Difficulty;
  guidance: string;
  reason: string;
  focus_errors: string[];
  suggested_resources: ResourceType[];
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
  adaptation?: AdaptationSnapshot | null;
}

export interface CitedText {
  text: string;
  citations: string[];
}
export type EducationalResource =
  | {
      resource_type: 'EXPLANATION';
      title: string;
      summary: CitedText;
      steps: CitedText[];
      worked_example: CitedText;
    }
  | {
      resource_type: 'EXERCISE';
      title: string;
      statement: CitedText;
      hints: CitedText[];
      solution_steps: CitedText[];
      answer: CitedText;
    }
  | {
      resource_type: 'QUIZ';
      title: string;
      questions: {
        statement: CitedText;
        options: string[];
        correct_option: number;
        explanation: CitedText;
      }[];
    }
  | {
      resource_type: 'FEEDBACK';
      title: string;
      diagnosis: CitedText;
      correction: CitedText;
      next_step: CitedText;
    };
export interface GenerationResponse {
  id: string;
  status: 'succeeded' | 'failed';
  resource: EducationalResource | null;
  message: string | null;
}
