// Recupera fuentes indexadas sin solicitar generación al proveedor.
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SearchResponse } from './busqueda.model';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  search(query: string, top_k: number, min_similarity: number, course: string) {
    return this.http.post<SearchResponse>('/api/v1/rag/search', {
      query,
      top_k,
      min_similarity,
      course,
    });
  }
}
