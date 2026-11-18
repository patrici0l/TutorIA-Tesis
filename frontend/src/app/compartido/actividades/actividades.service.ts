// Acceso HTTP único para ambos perfiles.
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  Assignment,
  AssignmentPage,
  AssignmentStatus,
  AssignmentSubmission,
} from './actividades.model';
@Injectable({ providedIn: 'root' })
export class AssignmentService {
  private readonly http = inject(HttpClient);
  list(offset = 0, limit = 10) {
    return this.http.get<AssignmentPage>('/api/v1/practice/assignments', {
      params: { offset, limit },
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
