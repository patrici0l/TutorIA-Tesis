import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { InicioComponent } from './inicio.component';

describe('InicioComponent', () => {
  let http: HttpTestingController;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InicioComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());

  it('muestra carga y los servicios disponibles', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Comprobando la conexión');
    http
      .expectOne('/api/v1/health')
      .flush({ status: 'ok', api: 'ok', database: 'ok', pgvector: 'ok', version: '0.1.0' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Conexión verificada');
    expect(fixture.nativeElement.querySelectorAll('.available').length).toBe(3);
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
    expect(fixture.nativeElement.textContent).toContain('hay servicios pendientes');
    expect(fixture.nativeElement.querySelectorAll('.available').length).toBe(1);
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
    expect(fixture.nativeElement.textContent).toContain('Conexión verificada');
  });

  it('rechaza respuestas que no cumplen el contrato', async () => {
    const fixture = TestBed.createComponent(InicioComponent);
    fixture.detectChanges();
    http.expectOne('/api/v1/health').flush({ message: 'not health' });
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('No se pudo conectar');
  });
});
