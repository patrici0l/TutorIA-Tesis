import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface PracticeResult {
  assignment_id?: string | null;
  id: string;
  version: string;
  answers: number[];
  score: number;
  created_at: string;
}
export interface PracticeProgress {
  items: PracticeResult[];
  total: number;
  best_score: number | null;
  offset: number;
  limit: number;
}
export const PRACTICE_VERSION = 'derivadas-v1';

@Injectable({ providedIn: 'root' })
export class PracticeService {
  private readonly http = inject(HttpClient);
  save(id: string, answers: number[], version = PRACTICE_VERSION, assignment_id?: string) {
    return this.http.post<PracticeResult>('/api/v1/practice/attempts', {
      id,
      version,
      assignment_id: assignment_id ?? null,
      answers,
    });
  }
  progress(offset = 0) {
    return this.http.get<PracticeProgress>('/api/v1/practice/attempts', {
      params: { offset, limit: 10 },
    });
  }
}
