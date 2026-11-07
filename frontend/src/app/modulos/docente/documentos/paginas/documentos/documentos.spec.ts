import { provideRouter } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { AuthService } from '../../../../../nucleo/servicios/auth.service';
import { DocumentsComponent } from './documentos';
import { CourseDocument } from '../../modelos/document.model';

describe('Documentos propios', () => {
  let http: HttpTestingController;
  const user = signal({ rol: 'teacher' });
  const sampleDocument: CourseDocument = {
    id: 'doc-1',
    title: 'Derivadas',
    filename: 'curso.txt',
    size_bytes: 24,
    mime_type: 'text/plain',
    status: 'uploaded',
    created_at: '2026-10-06T10:00:00Z',
    sha256: 'abc',
    processing_status: 'pending',
    processing_error: null,
    processed_at: null,
    processing_started_at: null,
    processing_version: null,
    chunk_chars: null,
    chunk_overlap: null,
    chunk_count: 0,
    text_chars: 0,
    index_status: 'pending',
    index_error: null,
    index_started_at: null,
    indexed_at: null,
    embedding_model: null,
    embedding_revision: null,
    embedding_version: null,
  };
  beforeEach(async () => {
    Object.defineProperty(HTMLDialogElement.prototype, 'showModal', {
      configurable: true,
      value() {
        this.setAttribute('open', '');
      },
    });
    Object.defineProperty(HTMLDialogElement.prototype, 'close', {
      configurable: true,
      value() {
        this.removeAttribute('open');
      },
    });
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [DocumentsComponent],
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
  function setup() {
    const fixture = TestBed.createComponent(DocumentsComponent);
    fixture.detectChanges();
    http
      .expectOne('/api/v1/documents?limit=20&offset=0')
      .flush({ items: [], total: 0, limit: 20, offset: 0 });
    return fixture;
  }
  it('limita el espacio docente sin consultar documentos para estudiantes', () => {
    user.set({ rol: 'student' });
    const fixture = TestBed.createComponent(DocumentsComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Espacio docente');
    http.expectNone('/api/v1/documents?limit=20&offset=0');
  });
  it('carga multipart, actualiza la biblioteca y consulta detalles', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    const input = fixture.nativeElement.querySelector('input[type=file]');
    component.file.set(new File(['derivadas'], 'curso.txt', { type: 'text/plain' }));
    component.title = 'Derivadas';
    component.course = 'Cálculo Diferencial';
    component.sourceReference = 'Muestra sintética';
    component.permissionNote = 'Prueba';
    component.authorizationConfirmed = true;
    component.upload(input);
    const upload = http.expectOne('/api/v1/documents/upload');
    expect(upload.request.body instanceof FormData).toBe(true);
    expect(upload.request.body.get('title')).toBe('Derivadas');
    upload.flush(sampleDocument);
    http.expectOne('/api/v1/documents/doc-1').flush(sampleDocument);
    http
      .expectOne('/api/v1/documents?limit=20&offset=0')
      .flush({ items: [sampleDocument], total: 1, limit: 20, offset: 0 });
    expect(component.file()).toBeNull();
    component.view(component.documents()[0]);
    http.expectOne('/api/v1/documents/doc-1').flush(sampleDocument);
    expect(component.selected()?.id).toBe('doc-1');
  });
  it('muestra errores de carga y permite volver a intentar', () => {
    const component = setup().componentInstance;
    component.file.set(new File(['derivadas'], 'curso.txt'));
    component.title = 'Derivadas';
    component.course = 'Cálculo Diferencial';
    component.sourceReference = 'Muestra sintética';
    component.permissionNote = 'Prueba';
    component.authorizationConfirmed = true;
    component.upload(document.createElement('input'));
    http
      .expectOne('/api/v1/documents/upload')
      .flush(
        { detail: 'Formato no permitido' },
        { status: 415, statusText: 'Unsupported Media Type' },
      );
    expect(component.error()).toBe('Formato no permitido');
    expect(component.busy()).toBe(false);
    expect(component.file()).not.toBeNull();
  });
  it('requiere selección para borrar y actualiza la lista tras eliminar', () => {
    const component = setup().componentInstance;
    component.remove();
    http.expectNone('/api/v1/documents/doc-1');
    component.pendingDelete.set(sampleDocument);
    component.remove();
    const request = http.expectOne('/api/v1/documents/doc-1');
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
    http
      .expectOne('/api/v1/documents?limit=20&offset=0')
      .flush({ items: [], total: 0, limit: 20, offset: 0 });
    expect(component.pendingDelete()).toBeNull();
    expect(component.success()).toBe('Documento eliminado.');
  });
  it('procesa el material y muestra sus fragmentos con referencias', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    component.documents.set([sampleDocument]);
    component.selected.set(sampleDocument);
    fixture.detectChanges();
    component.process();
    expect(component.locked()).toBe(true);
    const request = http.expectOne('/api/v1/documents/doc-1/process');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toBeNull();
    component.process();
    http.expectNone('/api/v1/documents/doc-1/process');
    request.flush({
      ...sampleDocument,
      processing_status: 'processed',
      chunk_count: 1,
      text_chars: 24,
    });
    fixture.detectChanges();
    http.expectOne('/api/v1/documents/doc-1/chunks?limit=10&offset=0').flush({
      items: [
        {
          id: 'chunk-1',
          position: 0,
          source_kind: 'paragraph',
          source_index: 2,
          char_start: 0,
          char_end: 24,
          text: 'La derivada es una razón.',
        },
      ],
      total: 1,
      limit: 10,
      offset: 0,
    });
    fixture.detectChanges();
    expect(component.locked()).toBe(false);
    expect(component.documents()[0].chunk_count).toBe(1);
    expect(fixture.nativeElement.textContent).toContain('Párrafo 2');
    expect(fixture.nativeElement.textContent).toContain('La derivada es una razón.');
    expect(fixture.nativeElement.textContent).toContain('texto extraído y dividido en 1 fragmento');
  });
  it('recupera el estado fallido del servidor y permite reintentar', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    component.selected.set(sampleDocument);
    component.process();
    http
      .expectOne('/api/v1/documents/doc-1/process')
      .flush(
        { detail: 'El documento no contiene texto extraíble.' },
        { status: 422, statusText: 'Unprocessable Entity' },
      );
    http.expectOne('/api/v1/documents/doc-1').flush({
      ...sampleDocument,
      processing_status: 'failed',
      processing_error: 'empty_text',
    });
    fixture.detectChanges();
    expect(component.processingId()).toBeNull();
    expect(component.error()).toBe('El documento no contiene texto extraíble.');
    expect(fixture.nativeElement.textContent).toContain('Reintentar procesamiento');
    component.process();
    http.expectOne('/api/v1/documents/doc-1/process').flush({
      ...sampleDocument,
      processing_status: 'processed',
      chunk_count: 1,
    });
    expect(component.selected()?.processing_status).toBe('processed');
  });
  it('conserva el nuevo detalle cuando termina el procesamiento de otro documento', () => {
    const component = setup().componentInstance;
    component.documents.set([sampleDocument]);
    component.selected.set(sampleDocument);
    component.process();
    const processing = http.expectOne('/api/v1/documents/doc-1/process');
    const second = { ...sampleDocument, id: 'doc-2', title: 'Límites' };
    component.view(second);
    http.expectOne('/api/v1/documents/doc-2').flush(second);
    processing.flush({ ...sampleDocument, processing_status: 'processed', chunk_count: 2 });
    expect(component.selected()?.id).toBe('doc-2');
    expect(component.documents()[0].processing_status).toBe('processed');
  });
  it('cancela el detalle anterior al elegir otro material', () => {
    const component = setup().componentInstance;
    component.view(sampleDocument);
    const previous = http.expectOne('/api/v1/documents/doc-1');
    const second = { ...sampleDocument, id: 'doc-2' };
    component.view(second);
    expect(previous.cancelled).toBe(true);
    http.expectOne('/api/v1/documents/doc-2').flush(second);
    expect(component.selected()?.id).toBe('doc-2');
  });
  it('indexa el texto procesado y conserva el nuevo detalle al terminar otro material', () => {
    const component = setup().componentInstance;
    const processed = { ...sampleDocument, processing_status: 'processed' as const };
    component.documents.set([processed]);
    component.selected.set(processed);
    component.index();
    const request = http.expectOne('/api/v1/documents/doc-1/index');
    expect(request.request.method).toBe('POST');
    expect(component.locked()).toBe(true);
    const second = { ...processed, id: 'doc-2' };
    component.view(second);
    http.expectOne('/api/v1/documents/doc-2').flush(second);
    request.flush({ ...processed, index_status: 'indexed' });
    expect(component.selected()?.id).toBe('doc-2');
    expect(component.documents()[0].index_status).toBe('indexed');
    expect(component.locked()).toBe(false);
  });
  it('conserva el error de índice del servidor y permite reintentar', () => {
    const component = setup().componentInstance;
    const processed = { ...sampleDocument, processing_status: 'processed' as const };
    component.selected.set(processed);
    component.index();
    http
      .expectOne('/api/v1/documents/doc-1/index')
      .flush({ detail: 'Modelo no preparado' }, { status: 503, statusText: 'Unavailable' });
    http
      .expectOne('/api/v1/documents/doc-1')
      .flush({ ...processed, index_status: 'failed', index_error: 'model_unavailable' });
    expect(component.error()).toBe('Modelo no preparado');
    expect(component.locked()).toBe(false);
    component.index();
    http
      .expectOne('/api/v1/documents/doc-1/index')
      .flush({ ...processed, index_status: 'indexed' });
    expect(component.selected()?.index_status).toBe('indexed');
  });
  it('reconstruye un índice únicamente con la acción explícita', () => {
    const component = setup().componentInstance;
    const indexed = {
      ...sampleDocument,
      processing_status: 'processed' as const,
      index_status: 'indexed' as const,
    };
    component.selected.set(indexed);
    component.index();
    http.expectNone('/api/v1/documents/doc-1/index');
    component.index(true);
    http.expectOne('/api/v1/documents/doc-1/index?rebuild=true').flush(indexed);
    expect(component.locked()).toBe(false);
  });
  it('permite recuperar un procesamiento interrumpido sin duplicar el que sigue activo', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    component.selected.set({
      ...sampleDocument,
      processing_status: 'processing',
      processing_started_at: new Date().toISOString(),
    });
    component.process();
    http.expectNone('/api/v1/documents/doc-1/process');
    component.selected.set({
      ...sampleDocument,
      processing_status: 'processing',
      processing_started_at: new Date(Date.now() - 180_000).toISOString(),
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Reintentar procesamiento');
    component.process();
    http.expectOne('/api/v1/documents/doc-1/process').flush({
      ...sampleDocument,
      processing_status: 'processed',
      chunk_count: 1,
    });
    expect(component.selected()?.processing_status).toBe('processed');
  });
  it('exige permiso y procedencia antes de cargar', () => {
    const component = setup().componentInstance;
    component.file.set(new File(['texto'], 'curso.txt'));
    component.title = 'Prueba';
    component.upload(document.createElement('input'));
    http.expectNone('/api/v1/documents/upload');
  });
  it('busca por asignatura sin solicitar IA y permite paginar', () => {
    const component = setup().componentInstance;
    component.filterCourse = 'Probabilidad y Estadística';
    component.textQuery = 'media';
    component.searchText();
    const request = http.expectOne((r) => r.url === '/api/v1/documents/text-search');
    expect(request.request.params.get('course')).toBe('Probabilidad y Estadística');
    expect(request.request.params.get('q')).toBe('media');
    request.flush({ items: [], total: 0, limit: 20, offset: 0 });
    expect(component.textResults()?.total).toBe(0);
  });
  it('cancela resultados pendientes cuando cambia el filtro', () => {
    const component = setup().componentInstance;
    component.filterCourse = 'Cálculo Diferencial';
    component.textQuery = 'derivada';
    component.searchText();
    const request = http.expectOne((r) => r.url === '/api/v1/documents/text-search');
    component.filterCourse = 'Probabilidad y Estadística';
    component.resetTextSearch();
    expect(request.cancelled).toBe(true);
    expect(component.textResults()).toBeNull();
    expect(component.searchingText()).toBe(false);
  });
  it('nueva versión exige confirmar nuevamente el permiso', () => {
    const component = setup().componentInstance;
    component.authorizationConfirmed = true;
    component.newVersion({ ...sampleDocument, course: 'Cálculo Diferencial', version_number: 2 });
    expect(component.previousVersionId).toBe(sampleDocument.id);
    expect(component.course).toBe('Cálculo Diferencial');
    expect(component.authorizationConfirmed).toBe(false);
  });
  it('abre carga solo al solicitarla y restaura foco y desplazamiento al cerrar', () => {
    const fixture = setup();
    fixture.detectChanges();
    const element = fixture.nativeElement as HTMLElement;
    const trigger = element.querySelector('.library-heading button') as HTMLButtonElement;
    const dialog = element.querySelector('dialog')!;
    expect(dialog.open).toBe(false);
    trigger.focus();
    trigger.click();
    fixture.detectChanges();
    expect(dialog.open).toBe(true);
    expect(fixture.componentInstance.panelMode()).toBe('upload');
    expect(document.body.style.overflow).toBe('hidden');
    dialog.dispatchEvent(new Event('cancel', { cancelable: true }));
    fixture.detectChanges();
    expect(dialog.open).toBe(false);
    expect(document.body.style.overflow).not.toBe('hidden');
    expect(document.activeElement).toBe(trigger);
  });
  it('muestra una sola cabecera y separa datos técnicos y origen del contenido', () => {
    const fixture = setup();
    fixture.componentInstance.view(sampleDocument);
    http.expectOne('/api/v1/documents/doc-1').flush(sampleDocument);
    fixture.detectChanges();
    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelectorAll('#drawer-title').length).toBe(1);
    expect(element.querySelector('[aria-label="Datos técnicos"]')).toBeNull();
    const buttons = element.querySelectorAll('.detail-sections button');
    (buttons[2] as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(element.querySelector('[aria-label="Datos técnicos"]')?.textContent).toContain(
      'SHA-256',
    );
    expect((element.querySelector('[aria-label="Contenido"]') as HTMLElement).hidden).toBe(true);
    (buttons[1] as HTMLButtonElement).click();
    fixture.detectChanges();
    expect(element.querySelector('[aria-label="Datos técnicos"]')).toBeNull();
    expect(element.querySelector('[aria-label="Origen y versiones"]')).toBeTruthy();
    fixture.componentInstance.closePanel();
  });
});
