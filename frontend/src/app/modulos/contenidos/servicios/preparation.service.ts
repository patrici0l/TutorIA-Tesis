import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  PreparationRequest,
  PreparationResponse,
  GenerationResponse,
} from '../modelos/preparation.model';

@Injectable({ providedIn: 'root' })
export class PreparationService {
  private readonly http = inject(HttpClient);
  generate(id: string) {
    return this.http.post<GenerationResponse>(`/api/v1/content/${id}/generate`, {});
  }
  prepare(request: PreparationRequest) {
    return this.http.post<PreparationResponse>('/api/v1/content/prepare', request);
  }
}
