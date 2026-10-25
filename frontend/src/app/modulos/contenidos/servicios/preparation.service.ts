// Distingue consultas de historial/cupo de las escrituras de preparación y generación.
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HistoryPage, HistoryDetail } from '../modelos/history.model';
import {
  PreparationRequest,
  PreparationResponse,
  GenerationResponse,
} from '../modelos/preparation.model';

export interface GenerationQuota {
  enabled: boolean;
  daily_limit: number;
  used: number;
  remaining: number;
  resets_at: string;
  max_output_tokens: number;
  timeout_seconds: number;
}

@Injectable({ providedIn: 'root' })
export class PreparationService {
  private readonly http = inject(HttpClient);
  quota() {
    return this.http.get<GenerationQuota>('/api/v1/content/quota');
  }
  history(offset = 0) {
    return this.http.get<HistoryPage>('/api/v1/content/history', { params: { offset, limit: 10 } });
  }
  detail(id: string) {
    return this.http.get<HistoryDetail>(`/api/v1/content/history/${id}`);
  }
  generate(id: string) {
    return this.http.post<GenerationResponse>(`/api/v1/content/${id}/generate`, {});
  }
  prepare(request: PreparationRequest) {
    return this.http.post<PreparationResponse>('/api/v1/content/prepare', request);
  }
}
