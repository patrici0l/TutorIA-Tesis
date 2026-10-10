import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { SearchComponent } from './search.component';

describe('Búsqueda de fuentes', () => {
  let http: HttpTestingController;
  const user = signal({ rol: 'teacher' });
  const response = {
    query: 'derivada',
    embedding_query: 'derivada',
    query_version: 'calculo-alias-v1',
    top_k: 5,
    min_similarity: 0,
    available_chunks: 1,
    method: 'exact_cosine',
    embedding_model: 'e5',
    embedding_revision: 'rev',
    embedding_version: 'v1',
    elapsed_ms: 100,
    results: [
      {
        id: 'c1',
        document_id: 'd1',
        document_title: 'Derivadas',
        filename: 'curso.txt',
        source_kind: 'paragraph',
        source_index: 1,
        position: 0,
        char_start: 0,
        char_end: 24,
        source_sha256: 'source-hash',
        document_sha256: 'file-hash',
        processing_version: 'v1',
        text: '<script>no ejecutar</script>',
        similarity: 0.85,
      },
    ],
  };
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [SearchComponent],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user } },
      ],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  it('busca con límites y muestra citas sin interpretar HTML', async () => {
    const fixture = TestBed.createComponent(SearchComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.query = 'derivada';
    component.search();
    expect(component.loading()).toBe(true);
    const request = http.expectOne('/api/v1/rag/search');
    expect(request.request.body).toEqual({ query: 'derivada', top_k: 5, min_similarity: 0 });
    component.search(); // A double submit must not create another inference.
    request.flush(response);
    await fixture.whenStable();
    expect(component.loading()).toBe(false);
    expect(fixture.nativeElement.querySelector('blockquote').textContent).toBe(
      response.results[0].text,
    );
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain('PÁRRAFO 1');
    expect(fixture.nativeElement.textContent).toContain('source-hash');
  });
  it('vacía resultados anteriores y permite reintentar un fallo', () => {
    const component = TestBed.createComponent(SearchComponent).componentInstance;
    component.query = 'derivada';
    component.search();
    http.expectOne('/api/v1/rag/search').flush(response);
    component.query = 'límite';
    component.search();
    expect(component.response()).toBeNull();
    http
      .expectOne('/api/v1/rag/search')
      .flush({ detail: 'El modelo está ocupado.' }, { status: 429, statusText: 'Busy' });
    expect(component.error()).toBe('El modelo está ocupado.');
    component.search();
    http.expectOne('/api/v1/rag/search').flush({ ...response, results: [], available_chunks: 0 });
    expect(component.response()?.results).toEqual([]);
  });
  it('evita consultas inválidas y acceso de estudiante', () => {
    const fixture = TestBed.createComponent(SearchComponent);
    const component = fixture.componentInstance;
    component.query = ' ';
    component.search();
    component.query = 'derivada';
    component.topK = 11;
    component.search();
    expect(component.error()).toBeTruthy();
    user.set({ rol: 'student' });
    component.topK = 5;
    component.search();
    fixture.detectChanges();
    http.expectNone('/api/v1/rag/search');
    expect(fixture.nativeElement.textContent).toContain('Espacio docente');
  });
});
