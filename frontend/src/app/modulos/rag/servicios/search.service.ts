import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { SearchResponse } from '../modelos/search.model';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);
  search(query: string, top_k: number, min_similarity: number) {
    return this.http.post<SearchResponse>('/api/v1/rag/search', { query, top_k, min_similarity });
  }
}
