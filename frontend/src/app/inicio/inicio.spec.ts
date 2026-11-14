import { By } from '@angular/platform-browser';
import { TeacherHomeComponent } from '../profesor/inicio';
import { signal } from '@angular/core';
import { provideRouter } from '@angular/router';
import { AuthService } from './sesion.service';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { InicioComponent } from './inicio';

describe('InicioComponent', () => {
  const user = signal({ rol: 'teacher' });
  let http: HttpTestingController;
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [InicioComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: AuthService, useValue: { user } },
      ],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());

  it('ofrece práctica al estudiante sin mostrar diagnósticos técnicos', async () => {
    user.set({ rol: 'student' });
    const fixture = TestBed.createComponent(InicioComponent);
    await fixture.whenStable();
    http.expectNone('/api/v1/health');
    expect(fixture.nativeElement.querySelector('a[href="/practica"]')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('a[href="/documentos"]')).toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain('Hito 01');
  });

  it('muestra carga y los servicios disponibles', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Comprobando la conexión');
    http
      .expectOne('/api/v1/health')
      .flush({ status: 'ok', api: 'ok', database: 'ok', pgvector: 'ok', version: '0.1.0' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Todo listo para trabajar');
    expect(fixture.nativeElement.querySelector('a[href="/documentos"]')).toBeTruthy();
  });

  it('distingue una API disponible de una base de datos caída', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    http.expectOne('/api/v1/health').flush(
      {
        status: 'degraded',
        api: 'ok',
        database: 'unavailable',
        pgvector: 'unavailable',
        version: '0.1.0',
      },
      { status: 503, statusText: 'Unavailable' },
    );
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Algunas funciones no están disponibles');
    expect(
      (
        fixture.debugElement.query(By.directive(TeacherHomeComponent))
          .componentInstance as TeacherHomeComponent
      ).health()?.api,
    ).toBe('ok');
  });

  it('permite reintentar después de un fallo de red', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    http.expectOne('/api/v1/health').error(new ProgressEvent('error'));
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('No se pudo conectar');
    fixture.nativeElement.querySelector('button').click();
    http
      .expectOne('/api/v1/health')
      .flush({ status: 'ok', api: 'ok', database: 'ok', pgvector: 'ok', version: '0.1.0' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Todo listo para trabajar');
  });

  it('rechaza respuestas que no cumplen el contrato', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    http.expectOne('/api/v1/health').flush({ message: 'not health' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('No se pudo conectar');
  });
});
