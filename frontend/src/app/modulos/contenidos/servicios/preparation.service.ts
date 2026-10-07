import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PreparationRequest, PreparationResponse } from '../modelos/preparation.model';

@Injectable({ providedIn: 'root' })
export class PreparationService {
  private readonly http = inject(HttpClient);
  prepare(request: PreparationRequest) {
    return this.http.post<PreparationResponse>('/api/v1/content/prepare', request);
  }
}
