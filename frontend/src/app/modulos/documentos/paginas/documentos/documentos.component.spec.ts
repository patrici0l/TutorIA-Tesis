import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { DocumentsComponent } from './documentos.component';

describe('Documentos propios', () => {
  let http: HttpTestingController;
  const user = signal({ rol: 'teacher' });
  const sampleDocument = {
    id: 'doc-1',
    title: 'Derivadas',
    filename: 'curso.txt',
    size_bytes: 24,
    mime_type: 'text/plain',
    status: 'uploaded',
    created_at: '2026-10-06T10:00:00Z',
    sha256: 'abc',
  };
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [DocumentsComponent],
      providers: [
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
    component.upload(input);
    const upload = http.expectOne('/api/v1/documents/upload');
    expect(upload.request.body instanceof FormData).toBe(true);
    expect(upload.request.body.get('title')).toBe('Derivadas');
    upload.flush(sampleDocument);
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
    component.pendingDelete.set(sampleDocument as never);
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
});
