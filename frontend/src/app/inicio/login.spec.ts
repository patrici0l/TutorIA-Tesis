import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, convertToParamMap, provideRouter, Router } from '@angular/router';
import { LoginComponent } from './login';

describe('Acceso según configuración del servidor', () => {
  async function render(error = false) {
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              queryParamMap: convertToParamMap(error ? { error: 'access_denied' } : {}),
            },
          },
        },
      ],
    }).compileComponents();
    const fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();
    return { fixture, http: TestBed.inject(HttpTestingController) };
  }
  afterEach(() => TestBed.inject(HttpTestingController).verify());

  it.each(['mock', 'cas'])(
    'muestra el acceso correcto sin campos de credenciales: %s',
    async (mode) => {
      const { fixture, http } = await render();
      http.expectOne('/api/v1/auth/me').flush({}, { status: 401, statusText: 'Unauthorized' });
      http.expectOne('/api/v1/auth/config').flush({ auth_mode: mode });
      fixture.detectChanges();
      const element = fixture.nativeElement as HTMLElement;
      expect(element.querySelectorAll('input').length).toBe(0);
      expect(element.querySelector('a')?.getAttribute('href')).toBe(
        mode === 'mock' ? '/api/v1/auth/login?demo_profile=student' : '/api/v1/auth/login',
      );
      expect(element.textContent).toContain(
        mode === 'mock' ? 'Entrar como estudiante' : 'Iniciar sesión con cuenta UPS',
      );
      if (mode === 'mock') expect(element.textContent).not.toContain('cuenta de prueba');
      expect(element.querySelectorAll('a').length).toBe(mode === 'mock' ? 2 : 1);
      if (mode === 'mock') {
        expect(element.querySelectorAll('a')[1].getAttribute('href')).toBe(
          '/api/v1/auth/login?demo_profile=teacher',
        );
        expect(element.textContent).toContain('Entrar como profesor');
      }
    },
  );

  it('restaura la sesión al abrir login directamente', async () => {
    const { fixture, http } = await render();
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigateByUrl').mockResolvedValue(true);
    http.expectOne('/api/v1/auth/me').flush({ auth_mode: 'mock', user: { nombre: 'Docente' } });
    expect(navigate).toHaveBeenCalledWith('/inicio');
    http.expectNone('/api/v1/auth/config');
    fixture.destroy();
  });

  it('permite recuperar un fallo de conexión sin enviar al callback', async () => {
    const { fixture, http } = await render();
    http.expectOne('/api/v1/auth/me').flush({}, { status: 503, statusText: 'Unavailable' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a')).toBeNull();
    fixture.nativeElement.querySelector('button').click();
    http.expectOne('/api/v1/auth/me').flush({}, { status: 401, statusText: 'Unauthorized' });
    http.expectOne('/api/v1/auth/config').flush({ auth_mode: 'mock' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('[role="alert"]')).toBeNull();
  });

  it('conserva el aviso de callback y muestra fallo de configuración', async () => {
    const { fixture, http } = await render(true);
    http.expectOne('/api/v1/auth/me').flush({}, { status: 401, statusText: 'Unauthorized' });
    http.expectOne('/api/v1/auth/config').flush({}, { status: 503, statusText: 'Unavailable' });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se pudo completar el acceso');
    expect(fixture.nativeElement.querySelector('a')).toBeNull();
    expect(fixture.nativeElement.querySelector('button')).not.toBeNull();
  });
});
