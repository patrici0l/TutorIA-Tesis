import { provideRouter } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ResourceHistoryComponent } from './historial';

describe('Historial privado', () => {
  it('consulta páginas y abre sin enviar una generación', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const fixture = TestBed.createComponent(ResourceHistoryComponent);
    const http = TestBed.inject(HttpTestingController);
    const component = fixture.componentInstance;
    let selected = '';
    component.selected.subscribe((detail) => (selected = detail.preparation.id));
    component.load();
    component.load();
    const page = http.expectOne('/api/v1/content/history?offset=0&limit=5');
    expect(page.request.method).toBe('GET');
    page.flush({ items: [], total: 12, offset: 0, limit: 5 });
    component.load(5);
    http
      .expectOne('/api/v1/content/history?offset=5&limit=5')
      .flush({ items: [], total: 12, offset: 5, limit: 5 });
    component.open('saved');
    const detail = http.expectOne('/api/v1/content/history/saved');
    expect(detail.request.method).toBe('GET');
    detail.flush({
      preparation: { id: 'saved' },
      status: 'succeeded',
      resource: null,
      message: null,
    });
    expect(selected).toBe('saved');
    http.expectNone((req) => req.method === 'POST');
    http.verify();
  });
  it('permite volver a consultar un fallo de lectura y respeta bloqueo', () => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    const fixture = TestBed.createComponent(ResourceHistoryComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.componentRef.setInput('locked', true);
    fixture.componentInstance.load();
    http.expectNone('/api/v1/content/history?offset=0&limit=5');
    fixture.componentRef.setInput('locked', false);
    fixture.componentInstance.load();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=5')
      .flush({}, { status: 503, statusText: 'Unavailable' });
    expect(fixture.componentInstance.error()).toContain('No se pudo cargar');
    fixture.componentInstance.load();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=5')
      .flush({ items: [], total: 0, offset: 0, limit: 5 });
    expect(fixture.componentInstance.error()).toBe('');
    http.verify();
  });
  it('permite elegir para asignar únicamente recursos generados, sin consumir IA', () => {
    TestBed.configureTestingModule({
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
    const fixture = TestBed.createComponent(ResourceHistoryComponent);
    fixture.componentRef.setInput('assignmentMode', true);
    fixture.componentInstance.page.set({
      items: ['prepared', 'succeeded', 'failed'].map((status, i) => ({
        id: 'r' + i,
        topic: 'Recurso ' + i,
        resource_type: 'EXPLANATION' as const,
        difficulty: 'basic' as const,
        status: status as 'prepared' | 'succeeded' | 'failed',
        created_at: '2026-11-12T20:00:00Z',
        completed_at: null,
      })),
      total: 3,
      offset: 0,
      limit: 5,
    });
    fixture.detectChanges();
    const links = fixture.nativeElement.querySelectorAll('a.action-link');
    expect(links.length).toBe(1);
    expect(links[0].textContent).toContain('Usar este recurso');
    expect(links[0].getAttribute('href')).toBe('/actividades?resource=r1');
    expect(fixture.nativeElement.textContent).toContain('Solo los recursos generados');
    TestBed.inject(HttpTestingController).expectNone(() => true);
  });
});
