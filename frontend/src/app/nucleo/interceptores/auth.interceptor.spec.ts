import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter, Router } from '@angular/router';
import { authInterceptor } from './auth.interceptor';

describe('Protección HTTP', () => {
  beforeEach(() => TestBed.configureTestingModule({providers: [provideRouter([]), provideHttpClient(withInterceptors([authInterceptor])), provideHttpClientTesting()]}));
  afterEach(() => TestBed.inject(HttpTestingController).verify());
  it('agrega cabecera CSRF a escrituras propias, sin token bearer', () => {
    TestBed.inject(HttpClient).post('/api/v1/example', {}).subscribe();
    const request = TestBed.inject(HttpTestingController).expectOne('/api/v1/example');
    expect(request.request.headers.get('X-TutorIA-Client')).toBe('web');
    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush({});
  });
  it('no envía la cabecera a otros dominios', () => {
    TestBed.inject(HttpClient).post('https://example.org/resource', {}).subscribe();
    const request = TestBed.inject(HttpTestingController).expectOne('https://example.org/resource');
    expect(request.request.headers.has('X-TutorIA-Client')).toBe(false);
    request.flush({});
  });
  it('redirige al acceso si una sesión es rechazada', () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    TestBed.inject(HttpClient).get('/api/v1/example').subscribe({error: () => {}});
    TestBed.inject(HttpTestingController).expectOne('/api/v1/example').flush({}, {status:401, statusText:'Unauthorized'});
    expect(navigate).toHaveBeenCalledWith('/login');
  });
});
