import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('Sesión con cookie', () => {
  let auth: AuthService;
  let http: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({providers: [provideHttpClient(), provideHttpClientTesting()]});
    auth = TestBed.inject(AuthService); http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  it('recupera la identidad desde me y cierra la sesión con protección CSRF', () => {
    auth.ensureSession().subscribe(ok => expect(ok).toBe(true));
    const request = http.expectOne('/api/v1/auth/me');
    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush({auth_mode: 'mock', user: {id: 'demo', nombre: 'Estudiante', rol: 'student'}});
    expect(auth.user()?.nombre).toBe('Estudiante');
    expect(auth.mode()).toBe('mock');
    auth.logout().subscribe();
    const logout = http.expectOne('/api/v1/auth/logout');
    expect(logout.request.headers.get('X-TutorIA-Client')).toBe('web');
    logout.flush(null);
    expect(auth.user()).toBeNull();
  });
  it('rechaza una sesión vencida', () => {
    auth.ensureSession().subscribe(ok => expect(ok).toBe(false));
    http.expectOne('/api/v1/auth/me').flush({detail: 'expired'}, {status: 401, statusText: 'Unauthorized'});
    expect(auth.user()).toBeNull();
    expect(auth.unavailable()).toBe(false);
  });
  it('distingue falta de sesión de fallo de conexión', () => {
    auth.ensureSession().subscribe(ok => expect(ok).toBe(false));
    http.expectOne('/api/v1/auth/me').error(new ProgressEvent('error'));
    expect(auth.unavailable()).toBe(true);
  });
});
