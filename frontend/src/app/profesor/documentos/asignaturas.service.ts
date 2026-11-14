import { inject, Injectable } from '@angular/core';
import { EMPTY, expand, map, reduce } from 'rxjs';
import { CourseDocument } from './documentos.model';
import { DocumentService } from './documentos.service';

export interface CourseOption {
  value: string;
  label: string;
  documents: number;
  enabled: number;
}

// Reúne todas las páginas del catálogo privado; no inventa asignaturas.
@Injectable({ providedIn: 'root' })
export class CourseCatalogService {
  private readonly documents = inject(DocumentService);

  load() {
    return this.documents.list(0).pipe(
      expand((page) =>
        page.items.length && page.offset + page.limit < page.total
          ? this.documents.list(page.offset + page.limit)
          : EMPTY,
      ),
      reduce((items, page) => [...items, ...page.items], [] as CourseDocument[]),
      map((documents) => {
        const courses = new Map<string, CourseOption>();
        for (const document of documents) {
          const value = document.course?.trim();
          if (!value || document.status !== 'uploaded') continue;
          const key = value.toLocaleLowerCase('es');
          const course = courses.get(key) ?? {
            value,
            label: value[0].toLocaleUpperCase('es') + value.slice(1),
            documents: 0,
            enabled: 0,
          };
          course.documents++;
          if (
            document.published_at &&
            document.permission_recorded_at &&
            document.processing_status === 'processed' &&
            document.index_status === 'indexed'
          )
            course.enabled++;
          courses.set(key, course);
        }
        return [...courses.values()].sort((a, b) => a.label.localeCompare(b.label, 'es'));
      }),
    );
  }
}
