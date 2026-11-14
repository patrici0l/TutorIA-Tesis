// Comprueba la sesión en servidor antes de activar rutas restringidas.
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map } from 'rxjs';
import { AuthService } from './sesion.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.ensureSession().pipe(map((ok) => ok || router.createUrlTree(['/login'])));
};
