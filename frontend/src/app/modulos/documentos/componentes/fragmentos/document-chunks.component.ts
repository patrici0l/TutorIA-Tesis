import { Component, inject, input, OnChanges, OnDestroy, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { DocumentChunk } from '../../modelos/document.model';
import { DocumentService } from '../../servicios/document.service';

@Component({
  selector: 'app-document-chunks',
  templateUrl: './document-chunks.component.html',
  styleUrl: './document-chunks.component.scss',
})
export class DocumentChunksComponent implements OnChanges, OnDestroy {
  readonly documentId = input.required<string>();
  private readonly service = inject(DocumentService);
  private request?: Subscription;
  readonly chunks = signal<DocumentChunk[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly total = signal(0);
  readonly offset = signal(0);

  ngOnChanges() {
    this.chunks.set([]);
    this.total.set(0);
    this.offset.set(0);
    this.load(0);
  }
  ngOnDestroy() {
    this.request?.unsubscribe();
  }
  load(offset = this.offset()) {
    this.request?.unsubscribe();
    this.loading.set(true);
    this.error.set('');
    this.request = this.service.chunks(this.documentId(), offset).subscribe({
      next: (page) => {
        this.chunks.set(page.items);
        this.total.set(page.total);
        this.offset.set(page.offset);
        this.loading.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.error.set(
          typeof error.error?.detail === 'string'
            ? error.error.detail
            : 'No se pudieron cargar los fragmentos. Inténtalo de nuevo.',
        );
        this.loading.set(false);
      },
    });
  }
}
