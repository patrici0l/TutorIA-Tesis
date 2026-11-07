import { Component, input, output } from '@angular/core';
import { CourseDocument } from '../../modelos/document.model';
import { processingLabel } from '../../modelos/document-labels';

// Presentación y paginación; las operaciones de documentos permanecen en el coordinador.
@Component({
  selector: 'app-document-library',
  templateUrl: './library.html',
  styleUrl: './library.scss',
})
export class DocumentLibraryComponent {
  readonly documents = input.required<CourseDocument[]>();
  readonly total = input.required<number>();
  readonly offset = input.required<number>();
  readonly loading = input(false);
  readonly locked = input(false);
  readonly busy = input(false);
  readonly processingId = input<string | null>(null);
  readonly reload = output<number>();
  readonly openDocument = output<CourseDocument>();
  processingLabel(document: CourseDocument) {
    return processingLabel(document, this.processingId());
  }
}
