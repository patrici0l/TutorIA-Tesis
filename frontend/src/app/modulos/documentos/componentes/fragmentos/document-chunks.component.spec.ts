import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { DocumentChunksComponent } from './document-chunks.component';

describe('Fragmentos de documentos', () => {
  let http: HttpTestingController;
  const chunk = {
    id: 'chunk-1',
    position: 0,
    source_kind: 'page',
    source_index: 3,
    char_start: 0,
    char_end: 20,
    text: '<img src=x onerror="alert(1)">',
  };
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentChunksComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  function setup() {
    const fixture = TestBed.createComponent(DocumentChunksComponent);
    fixture.componentRef.setInput('documentId', 'doc-1');
    fixture.detectChanges();
    return fixture;
  }
  it('renderiza el contenido como texto y pagina fragmentos con referencia a su origen', () => {
    const fixture = setup();
    http.expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=0').flush({
      items: [chunk],
      total: 11,
      limit: 10,
      offset: 0,
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('img')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain(chunk.text);
    expect(fixture.nativeElement.textContent).toContain('Página 3');
    const buttons: HTMLButtonElement[] = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    );
    expect(buttons[0].disabled).toBe(true);
    buttons[1].click();
    http.expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=10').flush({
      items: [{ ...chunk, id: 'chunk-11', source_kind: 'paragraph', source_index: 7 }],
      total: 11,
      limit: 10,
      offset: 10,
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Fragmento 11');
    expect(fixture.nativeElement.textContent).toContain('Párrafo 7');
    expect(fixture.nativeElement.querySelectorAll('button')[1].disabled).toBe(true);
  });
  it('cancela la carga al cambiar de documento y reinicia la página', () => {
    const fixture = setup();
    const previous = http.expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=0');
    fixture.componentRef.setInput('documentId', 'doc-2');
    fixture.detectChanges();
    expect(previous.cancelled).toBe(true);
    http.expectOne('/api/v1/documents/doc-2/chunks?limit=10&offset=0').flush({
      items: [],
      total: 0,
      limit: 10,
      offset: 0,
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.offset()).toBe(0);
    expect(fixture.nativeElement.textContent).toContain('No hay fragmentos disponibles');
  });
  it('muestra un error y permite recuperar la misma página', () => {
    const fixture = setup();
    http
      .expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=0')
      .flush({ detail: 'Documento no disponible.' }, { status: 404, statusText: 'Not Found' });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Documento no disponible.');
    fixture.nativeElement.querySelector('button').click();
    http.expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=0').flush({
      items: [chunk],
      total: 1,
      limit: 10,
      offset: 0,
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.error()).toBe('');
    expect(fixture.nativeElement.textContent).toContain('Página 3');
  });
});
