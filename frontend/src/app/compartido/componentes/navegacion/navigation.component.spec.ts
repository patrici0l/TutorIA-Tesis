import { Component, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { AuthService } from '../../../nucleo/servicios/auth.service';
import { NavigationComponent } from './navigation.component';

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
  it('abre con clic, oculta enlaces cerrados y Escape devuelve el foco', async () => {
    const fixture = await setup();
    const button = fixture.nativeElement.querySelector('.explore-trigger') as HTMLButtonElement;
    const panel = fixture.nativeElement.querySelector('.dropdown');
    expect(panel.hasAttribute('inert')).toBe(true);
    button.click();
    await fixture.whenStable();
    expect(button.getAttribute('aria-expanded')).toBe('true');
    expect(panel.hasAttribute('inert')).toBe(false);
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await fixture.whenStable();
    expect(button.getAttribute('aria-expanded')).toBe('false');
    expect(document.activeElement).toBe(button);
  });
  it('cierra al hacer clic fuera o mover el foco fuera de la navegación', async () => {
    const fixture = await setup();
    const component = fixture.componentInstance;
    component.toggle();
    await fixture.whenStable();
    document.body.click();
    await fixture.whenStable();
    expect(component.open()).toBe(false);
    component.toggle();
    component.focusOut(new FocusEvent('focusout', { relatedTarget: document.body }));
    expect(component.open()).toBe(false);
  });
  it('muestra destinos según el rol y acceso institucional cuando no hay sesión', async () => {
    const fixture = await setup();
    expect(fixture.componentInstance.items().length).toBe(4);
    user.set({ rol: 'student' });
    await fixture.whenStable();
    expect(fixture.componentInstance.items().map((item) => item.path)).toEqual(['/inicio']);
    user.set(null);
    await fixture.whenStable();
    expect(fixture.componentInstance.items().map((item) => item.path)).toEqual(['/login']);
  });
  it('marca la ruta activa y cierra el desplegable tras navegar', async () => {
    const fixture = await setup();
    const component = fixture.componentInstance;
    component.toggle();
    await TestBed.inject(Router).navigateByUrl('/documentos');
    await fixture.whenStable();
    expect(component.open()).toBe(false);
    const active = fixture.nativeElement.querySelector('.nav-tab[aria-current="page"]');
    expect(active.textContent).toContain('Documentos');
  });
  it('detecta los extremos del slider y desplaza sin movimiento si se solicita', async () => {
    const fixture = await setup();
    const component = fixture.componentInstance;
    const track = component.track()!.nativeElement;
    Object.defineProperties(track, {
      clientWidth: { value: 180, configurable: true },
      scrollWidth: { value: 420, configurable: true },
      scrollLeft: { value: 0, writable: true, configurable: true },
    });
    const scrollBy = vi.fn();
    track.scrollBy = scrollBy;
    const original = window.matchMedia;
    window.matchMedia = vi.fn().mockReturnValue({ matches: true });
    try {
      component.measure();
      expect(component.overflow()).toBe(true);
      expect(component.atStart()).toBe(true);
      expect(component.atEnd()).toBe(false);
      component.scroll(1);
      expect(scrollBy).toHaveBeenCalledWith({ left: 135, behavior: 'auto' });
      track.scrollLeft = 240;
      component.measure();
      expect(component.atStart()).toBe(false);
      expect(component.atEnd()).toBe(true);
    } finally {
      window.matchMedia = original;
    }
  });
});
