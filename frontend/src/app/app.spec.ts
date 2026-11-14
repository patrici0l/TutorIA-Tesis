import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';
import { provideHttpClient } from '@angular/common/http';
import { signal } from '@angular/core';
import { AuthService } from './inicio/sesion.service';
import { User } from './inicio/sesion.model';

describe('App', () => {
  const user = signal<User | null>(null);
  beforeEach(async () => {
    user.set(null);
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        { provide: AuthService, useValue: { user, mode: signal('mock') } },
      ],
    }).compileComponents();
  });
  it('conserva identidad y acceso al contenido sin mostrar Explorar antes de entrar', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('.skip-link')).toBeTruthy();
    expect(fixture.nativeElement.textContent).toContain('Recursos educativos');
    expect(fixture.nativeElement.querySelector('app-workspace-navigation')).toBeNull();
    expect(fixture.nativeElement.querySelector('.explore-trigger')).toBeNull();
  });
  it.each(['teacher', 'student'] as const)(
    'muestra Explorar para %s y lo retira al perder la sesión',
    async (rol) => {
      user.set({
        id: 'test-user',
        institutional_email: 'demo@example.org',
        institutional_id: null,
        nombre: 'Demo',
        apellido: '',
        rol,
        activo: true,
        created_at: '',
        last_login: '',
      });
      const fixture = TestBed.createComponent(App);
      await fixture.whenStable();
      expect(fixture.nativeElement.querySelector('.explore-trigger')).toBeTruthy();
      user.set(null);
      await fixture.whenStable();
      expect(fixture.nativeElement.querySelector('app-workspace-navigation')).toBeNull();
    },
  );
});
