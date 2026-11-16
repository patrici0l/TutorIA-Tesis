// Coordina carga, extracción e indexación sin confundir sus estados de preparación.
import {
  Component,
  computed,
  DestroyRef,
  ElementRef,
  inject,
  OnInit,
  signal,
  ViewChild,
} from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subscription } from 'rxjs';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { AuthService } from '../../inicio/sesion.service';
import { CourseCatalogService, CourseOption } from './asignaturas.service';
import { DocumentLibraryComponent } from './biblioteca';
import { processingLabel } from './documentos-etiquetas';
import { DocumentService } from './documentos.service';
import { SelectModule } from 'primeng/select';
import {
  CourseDocument,
  DocumentChunk,
  DOCUMENT_PAGE_SIZE,
  TextSearchPage,
} from './documentos.model';
import { DocumentChunksComponent } from './fragmentos';
@Component({
  selector: 'app-documents',
  imports: [
    FormsModule,
    DatePipe,
    RouterLink,
    SelectModule,
    DocumentChunksComponent,
    DocumentLibraryComponent,
  ],
  templateUrl: './documentos.html',
  styleUrl: './documentos.scss',
})
export class DocumentsComponent implements OnInit {
  private readonly attention = inject(ViewAttention);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);
  private readonly service = inject(DocumentService);
  private readonly courseCatalog = inject(CourseCatalogService);
  private readonly destroyRef = inject(DestroyRef);

  @ViewChild('documentPanel', { static: true }) private panel!: ElementRef<HTMLDialogElement>;

  // Estado del panel lateral (drawer) y secciones
  readonly panelMode = signal<'upload' | 'detail'>('detail');
  readonly detailSection = signal<'content' | 'origin' | 'technical'>('content');
  readonly reviewingFragments = signal(false);
  readonly selectedChunk = signal<DocumentChunk | null>(null);
  private panelTrigger: HTMLElement | null = null;
  private previousOverflow = '';

  // Estado de biblioteca y procesos asíncronos
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
  readonly appliedCourse = signal('');

  // Estado del formulario de subida y zona drag & drop
  readonly file = signal<File | null>(null);
  readonly dragging = signal(false);
  title = '';
  course = '';
  sourceReference = '';
  permissionNote = '';
  authorizationConfirmed = false;
  previousVersionId: string | undefined;

  // Estado de búsqueda semántica y filtros
  filterCourse: string | null = this.route.snapshot.queryParamMap.get('course') ?? '';
  readonly courseOptions = signal<CourseOption[]>([]);
  readonly loadingCourses = signal(false);
  textQuery = '';
  readonly textResults = signal<TextSearchPage | null>(null);
  readonly searchingText = signal(false);
  private textRequest?: Subscription;

  constructor() {
    this.destroyRef.onDestroy(() => {
      if (this.panel?.nativeElement.open) {
        this.panel.nativeElement.close();
        globalThis.document.body.style.overflow = this.previousOverflow;
      }
    });
  }

  ngOnInit() {
    if (this.canManage()) {
      this.load();
      this.loadCourseOptions();
    }
  }

  canManage() {
    return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? '');
  }

  // Navegación y mensajes de atención
  selectSection(section: 'content' | 'origin' | 'technical') {
    this.detailSection.set(section);
    this.attention.reveal('document-' + section);
  }

  confirmDelete(document: CourseDocument) {
    this.pendingDelete.set(document);
    this.attention.reveal('delete-title');
  }

  private showMessage() {
    const location = this.panel.nativeElement.open ? 'panel' : 'page';
    this.attention.reveal(`document-${location}-${this.error() ? 'error' : 'success'}`);
  }

  // Control de apertura y cierre del drawer
  openPanel(mode: 'upload' | 'detail') {
    this.panelMode.set(mode);
    const dialog = this.panel.nativeElement;
    if (!dialog.open) {
      this.panelTrigger = globalThis.document.activeElement as HTMLElement;
      this.previousOverflow = globalThis.document.body.style.overflow;
      globalThis.document.body.style.overflow = 'hidden';
      dialog.showModal();
    }
    dialog.scrollTop = 0;
    this.attention.reveal(mode === 'upload' ? 'document-title' : 'drawer-title');
  }

  openUpload() {
    this.detailRequest?.unsubscribe();
    this.detailLoading.set(false);
    this.previousVersionId = undefined;
    this.dragging.set(false);
    this.openPanel('upload');
  }

  closePanel() {
    if (this.busy()) return;
    this.closeDetails();
    this.pendingDelete.set(null);
    this.dragging.set(false);
    if (this.panel.nativeElement.open) {
      this.panel.nativeElement.close();
      globalThis.document.body.style.overflow = this.previousOverflow;
    }
    this.panelTrigger?.focus();
  }

  // Validación de metadatos y gestión de versiones
  metadataReady() {
    return !!(
      this.course.trim() &&
      this.sourceReference.trim() &&
      this.permissionNote.trim() &&
      this.authorizationConfirmed
    );
  }

  newVersion(document: CourseDocument) {
    this.openPanel('upload');
    this.previousVersionId = document.id;
    this.title = document.title;
    this.course = document.course ?? '';
    this.sourceReference = document.source_reference ?? '';
    this.permissionNote = document.permission_note ?? '';
    this.authorizationConfirmed = false;
    this.success.set('');
    this.file.set(null);
    this.dragging.set(false);
    const input = this.panel.nativeElement.querySelector<HTMLInputElement>('input[type=file]');
    if (input) input.value = '';
    this.pendingDelete.set(null);
  }

  openPrevious() {
    const item = this.selected();
    if (item?.previous_version_id) this.view({ ...item, id: item.previous_version_id });
  }

  // Búsqueda semántica en fragmentos
  resetTextSearch() {
    this.textRequest?.unsubscribe();
    this.textResults.set(null);
    this.searchingText.set(false);
  }

  searchText(offset = 0) {
    this.resetTextSearch();
    const course = this.filterCourse?.trim() ?? '';
    if (!course || !this.textQuery.trim()) {
      this.searchingText.set(false);
      this.error.set('Indica asignatura y texto para buscar.');
      this.showMessage();
      return;
    }
    this.searchingText.set(true);
    this.error.set('');
    this.textRequest = this.service
      .searchText(course, this.textQuery.trim(), offset)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          this.textResults.set(page);
          this.searchingText.set(false);
          this.attention.reveal('document-search-results');
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.searchingText.set(false);
        },
      });
  }

  // Listado paginado de documentos
  load(offset = this.offset(), reveal = false) {
    this.loading.set(true);
    this.error.set('');
    const course = this.filterCourse?.trim() ?? '';
    this.service
      .list(offset, course)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          this.documents.set(page.items);
          this.total.set(page.total);
          this.offset.set(offset);
          this.appliedCourse.set(course);
          this.loading.set(false);
          if (reveal) this.attention.reveal('library-title');
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.loading.set(false);
        },
      });
  }

  private loadCourseOptions() {
    this.loadingCourses.set(true);
    this.courseCatalog
      .load()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (courses) => {
          this.courseOptions.set(courses);
          const selectedCourse = this.filterCourse?.trim().toLocaleLowerCase('es');
          const match = courses.find(
            (course) => course.value.toLocaleLowerCase('es') === selectedCourse,
          );
          if (match) this.filterCourse = match.value;
          this.loadingCourses.set(false);
        },
        error: (error) => {
          this.loadingCourses.set(false);
          this.error.set(this.message(error));
          this.showMessage();
        },
      });
  }

  clearCourse() {
    this.filterCourse = '';
    this.resetTextSearch();
    this.load(0);
  }
  // Eventos de selección y arrastrar/soltar archivos
  onDragOver(event: DragEvent) {
    event.preventDefault();
    if (!this.locked()) this.dragging.set(true);
  }

  onDragLeave(event: DragEvent) {
    const zone = event.currentTarget as HTMLElement;
    if (event.relatedTarget instanceof Node && zone.contains(event.relatedTarget)) return;
    this.dragging.set(false);
  }

  onDrop(event: DragEvent, input: HTMLInputElement) {
    event.preventDefault();
    this.dragging.set(false);
    if (this.locked()) return;

    const droppedFile = event.dataTransfer?.files[0];
    if (droppedFile) this.selectFile(droppedFile, input);
  }

  choose(event: Event) {
    const input = event.target as HTMLInputElement;
    this.selectFile(input.files?.[0] ?? null, input);
  }

  private selectFile(file: File | null, input: HTMLInputElement) {
    this.error.set('');
    this.success.set('');
    this.file.set(null);

    if (!file) return;

    if (!/\.(pdf|docx|txt)$/i.test(file.name) || file.size === 0 || file.size > 10_485_760) {
      this.error.set('Selecciona un PDF, DOCX o TXT no vacío de hasta 10 MiB.');
      this.showMessage();
      input.value = '';
      return;
    }

    this.file.set(file);
    if (!this.title) this.title = file.name.replace(/\.[^.]+$/, '').slice(0, 160);
  }

  removeFile(input: HTMLInputElement) {
    this.file.set(null);
    input.value = '';
  }

  fileType(file: File) {
    return file.name.split('.').pop()?.toUpperCase() ?? 'FILE';
  }

  // Envío del archivo al backend
  upload(input: HTMLInputElement) {
    const file = this.file();
    if (!file || !this.title.trim() || !this.metadataReady() || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service
      .upload(file, this.title.trim(), {
        course: this.course.trim(),
        source_reference: this.sourceReference.trim(),
        permission_note: this.permissionNote.trim(),
        authorization_confirmed: this.authorizationConfirmed,
        previous_version_id: this.previousVersionId,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (saved) => {
          this.busy.set(false);
          this.file.set(null);
          this.title = '';
          this.previousVersionId = undefined;
          this.authorizationConfirmed = false;
          input.value = '';
          this.success.set(
            'Documento guardado. Abre sus detalles para extraer y segmentar el texto.',
          );
          this.load(0);
          this.view(saved);
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.busy.set(false);
        },
      });
  }

  // Carga de detalles del documento
  view(document: CourseDocument, chunk: DocumentChunk | null = null) {
    this.openPanel('detail');
    this.detailSection.set('content');
    this.selectedChunk.set(chunk);
    this.reviewingFragments.set(!!chunk);
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
          this.attention.reveal('drawer-title');
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.detailLoading.set(false);
        },
      });
  }

  closeDetails() {
    this.detailRequest?.unsubscribe();
    this.detailLoading.set(false);
    this.selected.set(null);
  }

  // Etapa 1: Extracción y segmentación de texto
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
            `«${item.title}»: texto extraído y dividido en ${item.chunk_count} ${item.chunk_count === 1 ? 'fragmento' : 'fragmentos'}. Continúa con Preparar para búsqueda.`,
          );
          if (this.panel.nativeElement.open && this.selected()?.id === item.id) {
            this.selectSection('content');
            this.attention.reveal('document-index');
          }
        },
        error: (error) => {
          this.processingId.set(null);
          this.error.set(this.message(error));
          this.showMessage();
          this.service
            .get(document.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (item) => this.updateDocument(item),
              error: () => { },
            });
        },
      });
  }

  processingLabel(document: CourseDocument) {
    return processingLabel(document, this.processingId());
  }

  canRetryProcessing(document: CourseDocument) {
    const started = Date.parse(document.processing_started_at ?? '');
    return (
      document.processing_status === 'processing' &&
      Number.isFinite(started) &&
      Date.now() - started >= 120_000
    );
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

  // Etapa 2: Indexación vectorial (Embeddings)
  canRetryIndex(document: CourseDocument) {
    const started = Date.parse(document.index_started_at ?? '');
    return (
      document.index_status === 'indexing' &&
      Number.isFinite(started) &&
      Date.now() - started >= 300_000
    );
  }

  indexLabel(document: CourseDocument) {
    if (this.indexingId() === document.id) return 'Preparando la búsqueda…';
    if (document.index_status === 'indexed') return 'Búsqueda preparada';
    if (document.index_status === 'indexing') return 'Preparación de búsqueda en curso';
    if (document.index_status === 'failed') return 'Preparación de búsqueda pendiente de reintento';
    return 'Búsqueda pendiente';
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
          this.success.set(
            `«${item.title}»: búsqueda preparada. Revisa los fragmentos y habilita esta versión.`,
          );
          if (this.panel.nativeElement.open && this.selected()?.id === item.id) {
            this.selectSection('content');
            this.attention.reveal('document-publication');
          }
        },
        error: (error) => {
          this.indexingId.set(null);
          this.error.set(this.message(error));
          this.showMessage();
          this.service
            .get(document.id)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (item) => this.updateDocument(item),
              error: () => { },
            });
        },
      });
  }

  // Etapa 3: Publicación / habilitación como fuente
  publication(publish: boolean) {
    const document = this.selected();
    if (!document || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service
      .publication(document.id, publish)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this.busy.set(false);
          this.updateDocument(item);
          this.success.set(
            publish
              ? 'Material habilitado para buscar y preparar recursos.'
              : 'Material retirado de nuevas búsquedas y generaciones.',
          );
          this.showMessage();
        },
        error: (error) => {
          this.busy.set(false);
          this.error.set(this.message(error));
          this.showMessage();
        },
      });
  }

  // Actualización en memoria y borrado
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
          this.closePanel();
          this.success.set('Documento eliminado.');
          this.showMessage();
          this.load(
            this.documents().length === 1 && this.offset() > 0 ? this.offset() - DOCUMENT_PAGE_SIZE : this.offset(),
          );
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.busy.set(false);
        },
      });
  }

  // Utilidades de formato y errores
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
