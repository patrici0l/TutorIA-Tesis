import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';
import { provideHttpClient } from '@angular/common/http';
import { signal } from '@angular/core';
import { AuthService } from './inicio/sesion.service';
import { User } from './inicio/sesion.model';
import { PracticeExitService } from './compartido/practica/salida-practica.service';
import { of } from 'rxjs';

describe('App', () => {
  const user = signal<User | null>(null);
  const logout = vi.fn(() => of(undefined));
  const canLeave = vi.fn<() => boolean | Promise<boolean>>(() => true);
  beforeEach(async () => {
    user.set(null);
    logout.mockClear();
    canLeave.mockReset().mockReturnValue(true);
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        { provide: AuthService, useValue: { user, mode: signal('mock'), logout } },
        { provide: PracticeExitService, useValue: { canLeave } },
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
  it('ajusta el espacio para el foco al cambiar la altura de la cabecera y libera el observador', async () => {
    let notifyResize = () => {};
    const observe = vi.fn();
    const disconnect = vi.fn();
    vi.stubGlobal('ResizeObserver', class {
      constructor(callback: ResizeObserverCallback) {
        notifyResize = () => callback([], {} as ResizeObserver);
      }
      observe = observe;
      disconnect = disconnect;
    });
    try {
      const fixture = TestBed.createComponent(App);
      await fixture.whenStable();
      const header = fixture.nativeElement.querySelector('.site-header') as HTMLElement;
      expect(observe).toHaveBeenCalledWith(header);
      const bounds = vi.spyOn(header, 'getBoundingClientRect');
      bounds.mockReturnValue({ height: 179.2 } as DOMRect);
      notifyResize();
      fixture.detectChanges();
      expect(fixture.nativeElement.style.getPropertyValue('--site-header-height')).toBe('180px');
      bounds.mockReturnValue({ height: 252 } as DOMRect);
      notifyResize();
      fixture.detectChanges();
      expect(fixture.nativeElement.style.getPropertyValue('--site-header-height')).toBe('252px');
      fixture.destroy();
      expect(disconnect).toHaveBeenCalledOnce();
    } finally {
      vi.unstubAllGlobals();
    }
  });
  it('conserva la sesión si se cancela la salida de una práctica pendiente', async () => {
    canLeave.mockReturnValue(false);
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    await fixture.componentInstance.logout();
    expect(logout).not.toHaveBeenCalled();
    expect(fixture.componentInstance.signingOut()).toBe(false);
    expect(fixture.componentInstance.checkingExit()).toBe(false);
  });
  it('espera la decisión de salida y no duplica el cierre de sesión', async () => {
    let resolveExit: (allowed: boolean) => void = () => {};
    canLeave.mockReturnValue(new Promise<boolean>((resolve) => { resolveExit = resolve; }));
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const navigate = vi.spyOn(fixture.componentInstance.router, 'navigateByUrl').mockResolvedValue(true);
    const first = fixture.componentInstance.logout();
    const second = fixture.componentInstance.logout();
    expect(logout).not.toHaveBeenCalled();
    resolveExit(true);
    await Promise.all([first, second]);
    expect(logout).toHaveBeenCalledOnce();
    expect(navigate).toHaveBeenCalledWith('/login');
  });
});
