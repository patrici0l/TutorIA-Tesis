import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { PracticeExitService, practiceExitGuard } from './salida-practica.service';

@Component({ template: '' })
class PracticePage {}

describe('Salida de una práctica pendiente', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [provideRouter([
      { path: 'practica', component: PracticePage, canDeactivate: [practiceExitGuard] },
      { path: 'inicio', component: PracticePage },
    ])],
  }));

  it('permite navegar sin práctica activa y retira solo el registro vigente', () => {
    const service = TestBed.inject(PracticeExitService);
    expect(service.canLeave()).toBe(true);
    const old = service.register(() => false);
    const current = service.register(() => false);
    old();
    expect(service.canLeave()).toBe(false);
    current();
    expect(service.canLeave()).toBe(true);
  });

  it('el guard conserva la ruta al cancelar y continúa tras una decisión explícita', async () => {
    const router = TestBed.inject(Router);
    const service = TestBed.inject(PracticeExitService);
    await RouterTestingHarness.create('/practica');
    service.register(() => false);
    expect(await router.navigateByUrl('/inicio')).toBe(false);
    expect(router.url).toBe('/practica');
    let resolve!: (allow: boolean) => void;
    service.register(() => new Promise<boolean>(decision => { resolve = decision; }));
    const navigation = router.navigateByUrl('/inicio');
    await new Promise(done => setTimeout(done, 0));
    expect(router.url).toBe('/practica');
    resolve(true);
    expect(await navigation).toBe(true);
    expect(router.url).toBe('/inicio');
  });
});
