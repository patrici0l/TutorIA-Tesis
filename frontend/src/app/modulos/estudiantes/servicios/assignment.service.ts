import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export type AssignmentStatus = 'open' | 'closed' | 'cancelled';
export const ASSIGNMENT_STATUS_LABELS: Record<AssignmentStatus, string> = {
  open: 'Abierta',
  closed: 'Cerrada',
  cancelled: 'Cancelada',
};

export interface Assignment {
  id: string;
  version: string;
  title: string;
  instructions: string;
  student_email: string;
  created_at: string;
  status: AssignmentStatus;
  status_changed_at: string | null;
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
  changeStatus(item: Assignment, status: AssignmentStatus) {
    return this.http.post<Assignment>(
      '/api/v1/practice/assignments/' + encodeURIComponent(item.id) + '/status',
      { status, expected_status: item.status },
    );
  }
}
