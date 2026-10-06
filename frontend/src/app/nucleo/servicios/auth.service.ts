import { inject, Injectable, signal } from '@angular/core';
import { HttpBackend, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, map, Observable, of, tap, throwError } from 'rxjs';
import { SessionResponse, User } from '../modelos/auth.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = new HttpClient(inject(HttpBackend));
  private readonly currentUser = signal<User | null>(null);
  readonly user = this.currentUser.asReadonly();
  readonly mode = signal<'mock' | 'cas' | null>(null);
  readonly unavailable = signal(false);

  clear() {
    this.currentUser.set(null);
    this.mode.set(null);
  }
  check(): Observable<SessionResponse> {
    return this.http.get<SessionResponse>('/api/v1/auth/me').pipe(
      tap((session) => {
        this.currentUser.set(session.user);
        this.mode.set(session.auth_mode);
        this.unavailable.set(false);
      }),
    );
  }
  ensureSession() {
    return this.check().pipe(
      map(() => true),
      catchError((error: HttpErrorResponse) => {
        this.clear();
        this.unavailable.set(error.status !== 401);
        return of(false);
      }),
    );
  }
  logout() {
    return this.http
      .post<void>('/api/v1/auth/logout', {}, { headers: { 'X-TutorIA-Client': 'web' } })
      .pipe(
        tap(() => this.clear()),
        catchError((error) => throwError(() => error)),
      );
  }
}
