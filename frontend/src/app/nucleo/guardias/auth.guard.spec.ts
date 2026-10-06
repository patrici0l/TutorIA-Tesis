import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, provideRouter, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { firstValueFrom, Observable, of } from 'rxjs';
import { AuthService } from '../servicios/auth.service';
import { authGuard } from './auth.guard';

describe('Rutas protegidas', () => {
  it.each([true, false])('solo permite entrar con sesión válida: %s', async (valid) => {
    TestBed.configureTestingModule({providers: [provideRouter([]), {provide: AuthService, useValue: {ensureSession: () => of(valid)}}]});
    const result = TestBed.runInInjectionContext(() => authGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot)) as Observable<boolean | UrlTree>;
    const value = await firstValueFrom(result);
    if (valid) expect(value).toBe(true);
    else expect(TestBed.inject(Router).serializeUrl(value as UrlTree)).toBe('/login');
  });
});
