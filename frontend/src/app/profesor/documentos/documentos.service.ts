// Centraliza operaciones HTTP de documentos; los permisos se validan en servidor.
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  DocumentList,
  CourseDocument,
  DocumentChunkList,
  DocumentMetadata,
  TextSearchPage,
} from './documentos.model';

@Injectable({ providedIn: 'root' })
export class DocumentService {
  private readonly http = inject(HttpClient);
  list(offset = 0, course = '') {
    return this.http.get<DocumentList>(
      `/api/v1/documents?limit=20&offset=${offset}${course ? '&course=' + encodeURIComponent(course) : ''}`,
    );
  }
  get(id: string) {
    return this.http.get<CourseDocument>(`/api/v1/documents/${id}`);
  }
  upload(file: File, title: string, metadata: DocumentMetadata) {
    const body = new FormData();
    body.append('file', file);
    body.append('title', title);
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== undefined) body.append(key, String(value));
    });
    return this.http.post<CourseDocument>('/api/v1/documents/upload', body);
  }
  searchText(course: string, query: string, offset = 0) {
    return this.http.get<TextSearchPage>('/api/v1/documents/text-search', {
      params: { course, q: query, limit: 20, offset },
    });
  }
  delete(id: string) {
    return this.http.delete<void>(`/api/v1/documents/${id}`);
  }
  process(id: string) {
    return this.http.post<CourseDocument>(`/api/v1/documents/${id}/process`, null);
  }
  index(id: string, rebuild = false) {
    return this.http.post<CourseDocument>(
      `/api/v1/documents/${id}/index${rebuild ? '?rebuild=true' : ''}`,
      null,
    );
  }
  publication(id: string, publish: boolean) {
    return this.http.post<CourseDocument>(
      `/api/v1/documents/${id}/${publish ? 'publish' : 'withdraw'}`,
      null,
    );
  }
  chunks(id: string, offset = 0) {
    return this.http.get<DocumentChunkList>(
      `/api/v1/documents/${id}/chunks?limit=10&offset=${offset}`,
    );
  }
}
