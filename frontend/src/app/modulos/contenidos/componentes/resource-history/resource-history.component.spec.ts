import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ResourceHistoryComponent } from './resource-history.component';

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
    const page = http.expectOne('/api/v1/content/history?offset=0&limit=10');
    expect(page.request.method).toBe('GET');
    page.flush({ items: [], total: 12, offset: 0, limit: 10 });
    component.load(10);
    http
      .expectOne('/api/v1/content/history?offset=10&limit=10')
      .flush({ items: [], total: 12, offset: 10, limit: 10 });
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
    http.expectNone('/api/v1/content/history?offset=0&limit=10');
    fixture.componentRef.setInput('locked', false);
    fixture.componentInstance.load();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=10')
      .flush({}, { status: 503, statusText: 'Unavailable' });
    expect(fixture.componentInstance.error()).toContain('No se pudo cargar');
    fixture.componentInstance.load();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=10')
      .flush({ items: [], total: 0, offset: 0, limit: 10 });
    expect(fixture.componentInstance.error()).toBe('');
    http.verify();
  });
});
