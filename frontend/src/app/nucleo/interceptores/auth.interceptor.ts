import { inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../servicios/auth.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (!request.url.startsWith('/api/v1/')) return next(request);
  const modifying = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method);
  const protectedRequest = modifying
    ? request.clone({ setHeaders: { 'X-TutorIA-Client': 'web' } })
    : request;
  return next(protectedRequest).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === 401) {
        auth.clear();
        void router.navigateByUrl('/login');
      }
      return throwError(() => error);
    }),
  );
};
