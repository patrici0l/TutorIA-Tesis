import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { LoginComponent } from './login.component';

describe('Acceso institucional', () => {
  async function render(error = false) {
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [provideHttpClient(), {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: convertToParamMap(error ? {error: 'access_denied'} : {})}}}],
    }).compileComponents();
    const fixture = TestBed.createComponent(LoginComponent);
    await fixture.whenStable();
    return fixture.nativeElement as HTMLElement;
  }
  it('ofrece solo el acceso al backend, sin correo ni contraseña', async () => {
    const element = await render();
    expect(element.querySelectorAll('input').length).toBe(0);
    expect(element.querySelector('a')?.getAttribute('href')).toBe('/api/v1/auth/login');
    expect(element.textContent).toContain('Iniciar sesión con cuenta UPS');
  });
  it('muestra un error seguro cuando falla el callback', async () => {
    const element = await render(true);
    expect(element.querySelector('[role="alert"]')?.textContent).toContain('No se pudo completar el acceso');
  });
});
