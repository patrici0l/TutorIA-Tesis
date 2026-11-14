import { ViewAttention } from '../../compartido/atencion-vista.service';
// Muestra fragmentos y referencias del documento seleccionado con paginación.
import {
  Component,
  ElementRef,
  inject,
  input,
  OnChanges,
  OnDestroy,
  signal,
  SimpleChanges,
} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { DocumentChunk } from './documentos.model';
import { DocumentService } from './documentos.service';

@Component({
  selector: 'app-document-chunks',
  templateUrl: './fragmentos.html',
  styleUrl: './fragmentos.scss',
})
export class DocumentChunksComponent implements OnChanges, OnDestroy {
  readonly documentId = input.required<string>();
  readonly active = input(true);
  readonly targetChunk = input<DocumentChunk | null>(null);
  private readonly attention = inject(ViewAttention);
  private readonly host: ElementRef<HTMLElement> = inject(ElementRef);
  private readonly service = inject(DocumentService);
  private request?: Subscription;
  readonly chunks = signal<DocumentChunk[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  readonly total = signal(0);
  readonly offset = signal(0);

  ngOnChanges(changes: SimpleChanges) {
    if (!this.active()) {
      this.request?.unsubscribe();
      this.loading.set(false);
      return;
    }
    this.chunks.set([]);
    this.total.set(0);
    this.offset.set(0);
    const target = this.targetChunk();
    this.load(
      target ? Math.floor(target.position / 10) * 10 : 0,
      !!target || (!!changes['active'] && !changes['active'].firstChange),
    );
  }
  ngOnDestroy() {
    this.request?.unsubscribe();
  }
  load(offset = this.offset(), reveal = false) {
    this.request?.unsubscribe();
    this.loading.set(true);
    this.error.set('');
    this.request = this.service.chunks(this.documentId(), offset).subscribe({
      next: (page) => {
        this.chunks.set(page.items);
        this.total.set(page.total);
        this.offset.set(page.offset);
        this.loading.set(false);
        if (reveal) this.revealPage();
      },
      error: (error: HttpErrorResponse) => {
        this.error.set(
          typeof error.error?.detail === 'string'
            ? error.error.detail
            : 'No se pudieron cargar los fragmentos. Inténtalo de nuevo.',
        );
        this.loading.set(false);
        if (reveal) this.revealPage();
      },
    });
  }
  private revealPage() {
    const id = this.targetChunk()?.id;
    if (id && this.chunks().some((chunk) => chunk.id === id))
      this.attention.reveal('document-chunk-' + id);
    else
      this.attention.reveal(this.host.nativeElement.querySelector<HTMLElement>('#chunks-title')!);
  }
}
