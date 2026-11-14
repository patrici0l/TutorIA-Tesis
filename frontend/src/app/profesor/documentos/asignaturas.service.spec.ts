import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { CourseDocument, DocumentList } from './documentos.model';
import { DocumentService } from './documentos.service';
import { CourseCatalogService } from './asignaturas.service';

describe('Asignaturas del catálogo privado', () => {
  it('recorre todas las páginas, agrupa materias y cuenta solo versiones habilitadas', () => {
    const document = {
      course: 'cálculo',
      status: 'uploaded',
      processing_status: 'processed',
      index_status: 'indexed',
      published_at: 'date',
      permission_recorded_at: 'date',
    } as CourseDocument;
    const list = vi.fn((offset: number) =>
      of({
        items: offset
          ? [
              { ...document, course: 'CÁLCULO', published_at: null },
              { ...document, course: 'probabilidad', index_status: 'pending' },
              { ...document, course: null },
            ]
          : [document],
        total: 4,
        offset,
        limit: offset ? 3 : 1,
      } as DocumentList),
    );
    TestBed.configureTestingModule({
      providers: [{ provide: DocumentService, useValue: { list } }],
    });
    let courses: unknown;
    TestBed.inject(CourseCatalogService)
      .load()
      .subscribe((value) => (courses = value));
    expect(list.mock.calls.map((call) => call[0])).toEqual([0, 1]);
    expect(courses).toEqual([
      { value: 'cálculo', label: 'Cálculo', documents: 2, enabled: 1 },
      { value: 'probabilidad', label: 'Probabilidad', documents: 1, enabled: 0 },
    ]);
  });

  it('no presenta un catálogo parcial si una página falla', () => {
    const list = vi.fn((offset: number) =>
      offset
        ? throwError(() => new Error('offline'))
        : of({ items: [{ course: 'Materia', status: 'uploaded' }], total: 2, offset: 0, limit: 1 }),
    );
    TestBed.configureTestingModule({
      providers: [{ provide: DocumentService, useValue: { list } }],
    });
    const next = vi.fn(),
      error = vi.fn();
    TestBed.inject(CourseCatalogService).load().subscribe({ next, error });
    expect(next).not.toHaveBeenCalled();
    expect(error).toHaveBeenCalledOnce();
  });
});
