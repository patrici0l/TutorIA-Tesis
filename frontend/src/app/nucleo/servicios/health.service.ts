import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, timeout } from 'rxjs';
import { environment } from '../../../environments/environment';
import { isHealthResponse } from '../modelos/health.model';

@Injectable({ providedIn: 'root' })
export class HealthService {
  private readonly http = inject(HttpClient);
  check() {
    return this.http.get<unknown>(`${environment.apiUrl}/health`).pipe(
      timeout(10000),
      map((result) => {
        if (!isHealthResponse(result)) throw new Error('Invalid health response');
        return result;
      }),
    );
  }
}
