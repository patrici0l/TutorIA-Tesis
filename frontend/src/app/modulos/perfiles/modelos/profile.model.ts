export type MasteryLevel = 'low' | 'medium' | 'high';
export type RecommendedSupport = 'reinforcement' | 'practice' | 'challenge';
export interface ProfileRequest {
  student_id: string;
  topic: string;
  performance: number;
  attempts: number;
  frequent_errors: string[];
  mastery_level: MasteryLevel;
  recommended_support: RecommendedSupport;
  data_kind: 'synthetic';
  resolution_time_seconds?: number;
  progress_trend?: 'improving' | 'stable' | 'declining';
}
export interface ProfileResponse extends ProfileRequest {
  id: string;
  created_at: string;
  schema_version: 'performance-profile-v1';
}
export interface ProfileSummary {
  id: string;
  student_id: string;
  topic: string;
  performance: number;
  mastery_level: MasteryLevel;
  created_at: string;
}
export interface ProfilePage {
  items: ProfileSummary[];
  total: number;
  offset: number;
  limit: number;
}
