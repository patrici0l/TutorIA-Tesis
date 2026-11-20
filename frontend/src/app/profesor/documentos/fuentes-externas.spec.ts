import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from '../../inicio/sesion.service';
import { ExternalSourcesComponent } from './fuentes-externas';

const base = '/api/v1/documents/external/wikipedia';
const preview = {
  source: { provider: 'wikipedia_es', page_id: 42, revision_id: 123, title: 'Derivada',
    url: 'https://es.wikipedia.org/w/index.php?oldid=123', text_sha256: 'a'.repeat(64),
    license_name: 'CC BY-SA 4.0', license_url: 'https://creativecommons.org/licenses/by-sa/4.0/',
    attribution: 'Colaboradores de Wikipedia', revision_at: '2026-11-19T12:00:00Z',
    retrieved_at: '2026-11-19T12:30:00Z' },
  text: '<script>no ejecutar</script> Texto del artículo', warnings: ['Revisa las fórmulas.'],
};

describe('Fuentes externas', () => {
  const user = signal({ rol: 'teacher' });
  let http: HttpTestingController;
  beforeEach(() => {
    user.set({ rol: 'teacher' });
    TestBed.configureTestingModule({ imports: [ExternalSourcesComponent], providers: [
      provideRouter([]), provideHttpClient(), provideHttpClientTesting(),
      { provide: AuthService, useValue: { user } },
    ] });
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());

  it('busca, revisa e importa la versión elegida sin enviar texto ni habilitarla', () => {
    const f = TestBed.createComponent(ExternalSourcesComponent), c = f.componentInstance;
    c.query = 'derivada'; c.search(); c.search();
    http.expectOne(base + '/search?q=derivada').flush([{ page_id: 42, title: 'Derivada' }]);
    c.review(c.results()[0]);
    http.expectOne(base + '/preview/42').flush(preview);
    f.detectChanges();
    expect(f.nativeElement.querySelector('script')).toBeNull();
    expect(f.nativeElement.textContent).toContain('<script>no ejecutar</script>');
    c.importArticle();
    http.expectNone(base + '/import');
    c.course = 'Cálculo Diferencial'; c.confirmed = true;
    c.importArticle(); c.importArticle();
    const req = http.expectOne(base + '/import');
    expect(req.request.body).toEqual({ page_id: 42, revision_id: 123,
      text_sha256: 'a'.repeat(64), course: 'Cálculo Diferencial', authorization_confirmed: true });
    req.flush({ id: 'doc', course: 'cálculo diferencial', published_at: null });
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('todavía no se utiliza');
    c.importArticle(); http.expectNone(base + '/import');
  });

  it('limpia una revisión anterior y exige confirmar cada artículo', () => {
    const c = TestBed.createComponent(ExternalSourcesComponent).componentInstance;
    c.review({ page_id: 42, title: 'Derivada' });
    http.expectOne(base + '/preview/42').flush(preview);
    c.confirmed = true;
    c.review({ page_id: 43, title: 'Límite' });
    expect(c.confirmed).toBe(false); expect(c.preview()).toBeNull();
    http.expectOne(base + '/preview/43').flush({ detail: 'Wikipedia no está disponible.' },
      { status: 503, statusText: 'Unavailable' });
    expect(c.busy()).toBe(false); expect(c.error()).toContain('no está disponible');
    expect(c.preview()).toBeNull();
  });

  it('muestra resultados vacíos y no permite consultas al estudiante', () => {
    const f = TestBed.createComponent(ExternalSourcesComponent), c = f.componentInstance;
    c.query = 'tema inexistente'; c.search();
    http.expectOne(base + '/search?q=tema%20inexistente').flush([]);
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('No se encontraron artículos');
    user.set({ rol: 'student' }); c.search(); c.review({ page_id: 42, title: 'Derivada' });
    f.detectChanges(); expect(f.nativeElement.textContent).toContain('Solo el profesor');
    http.expectNone(req => req.url.startsWith(base));
  });
});
