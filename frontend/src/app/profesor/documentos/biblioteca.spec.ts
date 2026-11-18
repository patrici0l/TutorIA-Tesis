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
