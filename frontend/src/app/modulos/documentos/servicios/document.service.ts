import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DocumentList, CourseDocument } from '../modelos/document.model';

@Injectable({ providedIn: 'root' })
export class DocumentService {
  private readonly http = inject(HttpClient);
  list(offset = 0) {
    return this.http.get<DocumentList>(`/api/v1/documents?limit=20&offset=${offset}`);
  }
  get(id: string) {
    return this.http.get<CourseDocument>(`/api/v1/documents/${id}`);
  }
  upload(file: File, title: string) {
    const body = new FormData();
    body.append('file', file);
    body.append('title', title);
    return this.http.post<CourseDocument>('/api/v1/documents/upload', body);
  }
  delete(id: string) {
    return this.http.delete<void>(`/api/v1/documents/${id}`);
  }
}
