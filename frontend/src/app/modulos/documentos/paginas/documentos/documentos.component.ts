import { Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subscription } from 'rxjs';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { DocumentService } from '../../servicios/document.service';
import { CourseDocument } from '../../modelos/document.model';
import { DocumentChunksComponent } from '../../componentes/fragmentos/document-chunks.component';

@Component({
  selector: 'app-documents',
  imports: [FormsModule, DatePipe, DocumentChunksComponent],
  templateUrl: './documentos.component.html',
  styleUrl: './documentos.component.scss',
})
export class DocumentsComponent implements OnInit {
  readonly auth = inject(AuthService);
  private readonly service = inject(DocumentService);
  private readonly destroyRef = inject(DestroyRef);
  private detailRequest?: Subscription;
  readonly documents = signal<CourseDocument[]>([]);
  readonly selected = signal<CourseDocument | null>(null);
  readonly pendingDelete = signal<CourseDocument | null>(null);
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly processingId = signal<string | null>(null);
  readonly indexingId = signal<string | null>(null);
  readonly detailLoading = signal(false);
  readonly locked = computed(
    () => this.busy() || this.processingId() !== null || this.indexingId() !== null,
  );
  readonly error = signal('');
  readonly success = signal('');
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly file = signal<File | null>(null);
  title = '';
  canManage() {
    return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? '');
  }
  ngOnInit() {
    if (this.canManage()) this.load();
  }
  load(offset = this.offset()) {
    this.loading.set(true);
    this.error.set('');
    this.service
      .list(offset)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          this.documents.set(page.items);
          this.total.set(page.total);
          this.offset.set(offset);
          this.loading.set(false);
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.loading.set(false);
        },
      });
  }
  choose(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.error.set('');
    this.success.set('');
    this.file.set(null);
    if (!file) return;
    if (!/\.(pdf|docx|txt)$/i.test(file.name) || file.size === 0 || file.size > 10_485_760) {
      this.error.set('Selecciona un PDF, DOCX o TXT no vacío de hasta 10 MiB.');
      input.value = '';
      return;
    }
    this.file.set(file);
    if (!this.title) this.title = file.name.replace(/\.[^.]+$/, '').slice(0, 160);
  }
  upload(input: HTMLInputElement) {
    const file = this.file();
    if (!file || !this.title.trim() || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service
      .upload(file, this.title.trim())
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy.set(false);
          this.file.set(null);
          this.title = '';
          input.value = '';
          this.success.set(
            'Documento guardado. Abre sus detalles para extraer y segmentar el texto.',
          );
          this.load(0);
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.busy.set(false);
        },
      });
  }
  view(document: CourseDocument) {
    this.detailRequest?.unsubscribe();
    this.selected.set(null);
    this.detailLoading.set(true);
    this.error.set('');
    this.detailRequest = this.service
      .get(document.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this.selected.set(item);
          this.detailLoading.set(false);
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.detailLoading.set(false);
        },
      });
  }
  closeDetails() {
    this.detailRequest?.unsubscribe();
    this.detailLoading.set(false);
    this.selected.set(null);
  }
  process() {
    const document = this.selected();
    if (
      !document ||
      this.locked() ||
      document.processing_status === 'processed' ||
      (document.processing_status === 'processing' && !this.canRetryProcessing(document))
    )
      return;
    this.processingId.set(document.id);
    this.error.set('');
    this.success.set('');
    this.service
      .process(document.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this.processingId.set(null);
          this.updateDocument(item);
          this.success.set(
            `«${item.title}»: texto extraído y dividido en ${item.chunk_count} ${item.chunk_count === 1 ? 'fragmento' : 'fragmentos'}.`,
          );
        },
        error: (error) => {
          this.processingId.set(null);
          this.error.set(this.message(error));
          this.service
            .get(document.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (item) => this.updateDocument(item),
              error: () => {},
            });
        },
      });
  }
  processingLabel(document: CourseDocument) {
    if (this.processingId() === document.id) return 'Extrayendo y segmentando…';
    switch (document.processing_status) {
      case 'processing':
        return 'Procesamiento en curso';
      case 'processed':
        return `${document.chunk_count} ${document.chunk_count === 1 ? 'fragmento' : 'fragmentos'} · Texto procesado`;
      case 'failed':
        return 'No se pudo procesar · Puedes reintentar';
      default:
        return 'Guardado · Pendiente de procesamiento';
    }
  }
  canRetryProcessing(document: CourseDocument) {
    const started = Date.parse(document.processing_started_at ?? '');
    return (
      document.processing_status === 'processing' &&
      Number.isFinite(started) &&
      Date.now() - started >= 120_000
    );
  }
  canRetryIndex(document: CourseDocument) {
    const started = Date.parse(document.index_started_at ?? '');
    return (
      document.index_status === 'indexing' &&
      Number.isFinite(started) &&
      Date.now() - started >= 300_000
    );
  }
  indexLabel(document: CourseDocument) {
    if (this.indexingId() === document.id) return 'Generando el índice local…';
    if (document.index_status === 'indexed') return 'Índice vectorial listo';
    if (document.index_status === 'indexing') return 'Indexación en curso';
    if (document.index_status === 'failed') return 'Indexación pendiente de reintento';
    return 'Pendiente de indexar';
  }
  indexError(document: CourseDocument) {
    const messages: Record<string, string> = {
      model_unavailable:
        'El modelo local no está preparado o no supera la verificación de integridad.',
      token_limit:
        'Un fragmento supera el límite del modelo. El material requiere una segmentación más pequeña.',
      embedding_timeout: 'La indexación tardó demasiado. Prueba con menos material.',
      invalid_embedding: 'El modelo produjo un resultado inválido; no se guardó un índice parcial.',
    };
    return (
      messages[document.index_error ?? ''] ?? 'No se pudo indexar el material. Puedes reintentarlo.'
    );
  }
  index(rebuild = false) {
    const document = this.selected();
    if (
      !document ||
      this.locked() ||
      document.processing_status !== 'processed' ||
      (document.index_status === 'indexed' && !rebuild) ||
      (document.index_status === 'indexing' && !this.canRetryIndex(document))
    )
      return;
    this.indexingId.set(document.id);
    this.error.set('');
    this.success.set('');
    this.service
      .index(document.id, rebuild)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this.indexingId.set(null);
          this.updateDocument(item);
          this.success.set(`«${item.title}»: índice vectorial preparado en tu equipo.`);
        },
        error: (error) => {
          this.indexingId.set(null);
          this.error.set(this.message(error));
          this.service
            .get(document.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (item) => this.updateDocument(item),
              error: () => {},
            });
        },
      });
  }
  processingError(document: CourseDocument) {
    const messages: Record<string, string> = {
      empty_text: 'No se encontró texto extraíble. Un PDF escaneado necesita OCR.',
      unsupported_document:
        'OfficeMath y algunos estilos matemáticos requieren una conversión previa.',
      invalid_document: 'No se pudo leer la estructura del documento.',
      extraction_limit: 'El documento supera los límites de texto, páginas o fragmentos.',
      file_missing: 'El archivo privado no está disponible. Vuelve a cargar el documento.',
      file_unavailable: 'No se pudo acceder al archivo privado de forma segura.',
      file_changed: 'El archivo no coincide con la copia cargada. Vuelve a cargar el documento.',
      extraction_timeout: 'La extracción tardó demasiado. Prueba con un documento más pequeño.',
    };
    return (
      messages[document.processing_error ?? ''] ??
      'El procesamiento anterior no se completó. Puedes volver a intentarlo.'
    );
  }
  private updateDocument(document: CourseDocument) {
    this.documents.update((items) =>
      items.map((item) => (item.id === document.id ? document : item)),
    );
    if (this.selected()?.id === document.id) this.selected.set(document);
  }
  remove() {
    const document = this.pendingDelete();
    if (!document || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service
      .delete(document.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.busy.set(false);
          this.pendingDelete.set(null);
          this.closeDetails();
          this.success.set('Documento eliminado.');
          this.load(
            this.documents().length === 1 && this.offset() > 0 ? this.offset() - 20 : this.offset(),
          );
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.busy.set(false);
        },
      });
  }
  size(bytes: number) {
    return `${(bytes / 1024).toFixed(1)} KiB`;
  }
  private message(error: HttpErrorResponse) {
    const detail = error.error?.detail;
    return typeof detail === 'string'
      ? detail
      : 'No se pudo completar la operación. Revisa la conexión e inténtalo de nuevo.';
  }
}
