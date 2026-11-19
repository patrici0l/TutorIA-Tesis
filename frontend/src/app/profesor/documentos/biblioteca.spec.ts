import { TestBed } from '@angular/core/testing';
import { DocumentLibraryComponent } from './biblioteca';
import { CourseDocument, DOCUMENT_PAGE_SIZE } from './documentos.model';
it('conserva documento seleccionado y límites al delegar apertura y paginación', async () => {
  await TestBed.configureTestingModule({ imports: [DocumentLibraryComponent] }).compileComponents();
  const f = TestBed.createComponent(DocumentLibraryComponent);
  const item = {
    id: 'd1',
    title: 'Material',
    version_number: 1,
    processing_status: 'pending',
  } as CourseDocument;
  f.componentRef.setInput('documents', [item]);
  f.componentRef.setInput('total', 21);
  f.componentRef.setInput('offset', 0);
  f.detectChanges();
  const open = vi.fn(),
    reload = vi.fn();
  f.componentInstance.openDocument.subscribe(open);
  f.componentInstance.reload.subscribe(reload);
  (f.nativeElement.querySelector('.document-list button') as HTMLButtonElement).click();
  expect(open).toHaveBeenCalledWith(item);
  const buttons = f.nativeElement.querySelectorAll('.pagination button');
  expect(buttons[0].disabled).toBe(true);
  buttons[1].click();
  expect(reload).toHaveBeenCalledWith(DOCUMENT_PAGE_SIZE);
});

it('distingue extracción, índice y habilitación sin atribuir una retirada no registrada', async () => {
  await TestBed.configureTestingModule({ imports: [DocumentLibraryComponent] }).compileComponents();
  const fixture = TestBed.createComponent(DocumentLibraryComponent);
  const processed = {
    id: 'not-enabled',
    title: 'Procesado sin habilitar',
    processing_status: 'processed',
    chunk_count: 1,
    index_status: 'pending',
    published_at: null,
  } as CourseDocument;
  fixture.componentRef.setInput('documents', [
    processed,
    { ...processed, id: 'enabled', title: 'Fuente lista', index_status: 'indexed', published_at: '2026-11-19T10:00:00Z' },
    { ...processed, id: 'failed', title: 'Índice fallido', index_status: 'failed' },
  ]);
  fixture.componentRef.setInput('total', 3);
  fixture.componentRef.setInput('offset', 0);
  fixture.detectChanges();
  const rows = fixture.nativeElement.querySelectorAll('.document-row') as NodeListOf<HTMLElement>;
  expect(rows[0].textContent).toContain('Texto procesado');
  expect(rows[0].textContent).toContain('Índice pendiente');
  expect(rows[0].textContent).toContain('Sin habilitar');
  expect(rows[1].textContent).toContain('Índice preparado');
  expect(rows[1].textContent).toContain('Habilitado para recursos');
  expect(rows[2].textContent).toContain('Índice con error');
  expect(rows[2].querySelector('.index-state')?.classList.contains('badge-error')).toBe(true);
  expect(fixture.nativeElement.textContent).not.toContain('Retirado');
});
