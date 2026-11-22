import { Component, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { AuthService } from '../../inicio/sesion.service';
import { NavigationComponent } from './navegacion';

@Component({ template: '' })
class EmptyPage {}

describe('Navegación superior', () => {
  const user = signal<{ rol: string } | null>({ rol: 'teacher' });
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [NavigationComponent],
      providers: [
        provideRouter([
          { path: 'inicio', component: EmptyPage },
          { path: 'documentos', component: EmptyPage },
        ]),
        { provide: AuthService, useValue: { user } },
      ],
    }).compileComponents();
  });
  async function setup() {
    const fixture = TestBed.createComponent(NavigationComponent);
    await fixture.whenStable();
    return fixture;
  }
  it('abre un diálogo modal y Escape devuelve el foco', async () => {
    const fixture = await setup();
    const button = fixture.nativeElement.querySelector('.explore-trigger') as HTMLButtonElement;
    const panel = fixture.nativeElement.querySelector('dialog') as HTMLDialogElement;
    panel.showModal = vi.fn(() => panel.setAttribute('open', ''));
    panel.close = vi.fn(() => panel.removeAttribute('open'));
    button.click();
    await fixture.whenStable();
    expect(panel.showModal).toHaveBeenCalled();
    expect(button.getAttribute('aria-expanded')).toBe('true');
    panel.dispatchEvent(new Event('cancel', { cancelable: true }));
    await fixture.whenStable();
    expect(panel.open).toBe(false);
    expect(button.getAttribute('aria-expanded')).toBe('false');
    expect(document.activeElement).toBe(button);
  });
  it('cierra desde el fondo y no duplica destinos con un carrusel', async () => {
    const fixture = await setup();
    const panel = fixture.nativeElement.querySelector('dialog') as HTMLDialogElement;
    panel.showModal = vi.fn();
    panel.close = vi.fn();
    fixture.componentInstance.toggle();
    panel.click();
    await fixture.whenStable();
    expect(fixture.componentInstance.open()).toBe(false);
    expect(fixture.nativeElement.querySelectorAll('nav').length).toBe(1);
    expect(fixture.nativeElement.querySelector('.slider')).toBeNull();
  });
  it('muestra destinos según el rol y ninguno cuando no hay sesión', async () => {
    const fixture = await setup();
    expect(fixture.componentInstance.items().map((item) => item.path)).toContain('/metricas');
    user.set({ rol: 'student' });
    await fixture.whenStable();
    expect(fixture.componentInstance.items().map((item) => item.path)).toEqual([
      '/inicio',
      '/solicitar',
      '/actividades',
      '/practica',
    ]);
    user.set(null);
    await fixture.whenStable();
    expect(fixture.componentInstance.items()).toEqual([]);
  });
  it('marca la ruta activa y cierra el desplegable tras navegar', async () => {
    const fixture = await setup();
    const component = fixture.componentInstance;
    const panel = fixture.nativeElement.querySelector('dialog');
    panel.showModal = vi.fn();
    panel.close = vi.fn();
    component.toggle();
    await TestBed.inject(Router).navigateByUrl('/documentos');
    await fixture.whenStable();
    expect(component.open()).toBe(false);
    const active = fixture.nativeElement.querySelector('a[aria-current="page"]');
    expect(active.textContent).toContain('Mis documentos');
  });
});
