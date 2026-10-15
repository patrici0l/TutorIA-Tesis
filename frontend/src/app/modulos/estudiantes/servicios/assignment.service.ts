import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Assignment {
  id: string;
  version: string;
  title: string;
  instructions: string;
  student_email: string;
  created_at: string;
  attempts: number;
  best_score: number | null;
}
export interface AssignmentPage {
  items: Assignment[];
  total: number;
  offset: number;
  limit: number;
}
export interface AssignmentSubmission {
  id: string;
  student_email: string;
  version: string;
  title: string;
  instructions: string;
}
@Injectable({ providedIn: 'root' })
export class AssignmentService {
  private readonly http = inject(HttpClient);
  list(offset = 0) {
    return this.http.get<AssignmentPage>('/api/v1/practice/assignments', {
      params: { offset, limit: 10 },
    });
  }
  detail(id: string) {
    return this.http.get<Assignment>('/api/v1/practice/assignments/' + encodeURIComponent(id));
  }
  create(body: AssignmentSubmission) {
    return this.http.post<Assignment>('/api/v1/practice/assignments', body);
  }
}
