import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MetricsSummary } from '../modelos/metrics.model';

@Injectable({ providedIn: 'root' })
export class MetricsService {
  private readonly http = inject(HttpClient);
  summary() {
    return this.http.get<MetricsSummary>('/api/v1/metrics');
  }
}
