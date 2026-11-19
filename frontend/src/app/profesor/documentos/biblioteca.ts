import { Component, input, output } from '@angular/core';
import { CourseDocument, DOCUMENT_PAGE_SIZE } from './documentos.model';
import { indexLabel, processingLabel } from './documentos-etiquetas';

// Presentación y paginación; las operaciones de documentos permanecen en el coordinador.
@Component({
  selector: 'app-document-library',
  templateUrl: './biblioteca.html',
  styleUrl: './biblioteca.scss',
})
export class DocumentLibraryComponent {
  readonly selectedId = input<string | null>(null);
  readonly documents = input.required<CourseDocument[]>();
  readonly courseFilter = input('');
  readonly pageSize = DOCUMENT_PAGE_SIZE;
  readonly total = input.required<number>();
  readonly offset = input.required<number>();
  readonly loading = input(false);
  readonly locked = input(false);
  readonly busy = input(false);
  readonly processingId = input<string | null>(null);
  readonly reload = output<number>();
  readonly openDocument = output<CourseDocument>();
  readonly clearCourseFilter = output<void>();
  readonly indexLabel = indexLabel;
  processingLabel(document: CourseDocument) {
    return processingLabel(document, this.processingId());
  }
}

