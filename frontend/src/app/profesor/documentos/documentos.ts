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
import { NgOptionTemplateDirective, NgSelectComponent } from '@ng-select/ng-select';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, concatMap, from, map, Observable, of, Subscription, switchMap, tap, toArray } from 'rxjs';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { AuthService } from '../../inicio/sesion.service';
import { CourseCatalogService, CourseOption } from './asignaturas.service';
import { DocumentLibraryComponent } from './biblioteca';
import { processingLabel } from './documentos-etiquetas';
import { DocumentService } from './documentos.service';
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
    NgSelectComponent,
    NgOptionTemplateDirective,
    DocumentChunksComponent,
    DocumentLibraryComponent,
  ],
  templateUrl: './documentos.html',
  styleUrls: ['./documentos.scss', './documentos-panel.scss', './asignaturas.scss'],
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
  readonly publicationReviewed = signal(false);
  readonly selectedChunk = signal<DocumentChunk | null>(null);
  private panelTrigger: HTMLElement | null = null;
  private previousOverflow = '';

  // Estado de biblioteca y procesos asíncronos
  private detailRequest?: Subscription;
  private listRequest?: Subscription;
  readonly documents = signal<CourseDocument[]>([]);
  readonly selected = signal<CourseDocument | null>(null);
  readonly pendingDelete = signal<CourseDocument | null>(null);
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly processingId = signal<string | null>(null);
  readonly indexingId = signal<string | null>(null);
  readonly autoPreparing = signal(false);
  readonly detailLoading = signal(false);
  readonly locked = computed(
    () =>
      this.busy() ||
      this.autoPreparing() ||
      this.processingId() !== null ||
      this.indexingId() !== null,
  );
  readonly pendingDocuments = computed(() =>
    this.documents().filter(
      (doc) =>
        doc.status === 'uploaded' &&
        !doc.published_at &&
        doc.index_status !== 'indexed' &&
        !!doc.permission_recorded_at &&
        !!doc.course,
    ),
  );
  readonly error = signal('');
  readonly success = signal('');
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly appliedCourse = signal('');

  // Estado del formulario de subida y zona drag & drop (admite uno o varios archivos por materia)
  readonly file = signal<File | null>(null);
  readonly extraFiles = signal<File[]>([]);
  readonly selectedFiles = computed(() => {
    const primary = this.file();
    return primary ? [primary, ...this.extraFiles()] : [];
  });
  readonly dragging = signal(false);
  title = '';
  course = '';
  sourceReference = '';
  permissionNote = '';
  authorizationConfirmed = false;
  autoPrepareOnUpload = false;
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

  openUpload(prefillCourse?: CourseDocument) {
    this.detailRequest?.unsubscribe();
    this.detailLoading.set(false);
    this.previousVersionId = undefined;
    this.dragging.set(false);
    if (prefillCourse) {
      this.course = prefillCourse.course ?? this.course;
      this.sourceReference = prefillCourse.source_reference ?? this.sourceReference;
      this.permissionNote = prefillCourse.permission_note ?? this.permissionNote;
      this.title = '';
      this.file.set(null);
      this.extraFiles.set([]);
    } else if (!this.course.trim() && this.filterCourse?.trim()) {
      this.course = this.filterCourse.trim();
    }
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
    this.extraFiles.set([]);
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
    this.listRequest?.unsubscribe();
    this.loading.set(true);
    this.error.set('');
    const course = this.filterCourse?.trim() ?? '';
    this.listRequest = this.service
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

    const droppedFiles = Array.from(event.dataTransfer?.files ?? []);
    if (droppedFiles.length) this.selectFiles(droppedFiles, input);
  }

  choose(event: Event) {
    const input = event.target as HTMLInputElement;
    const chosen = Array.from(input.files ?? []);
    this.selectFiles(chosen, input);
  }

  private selectFiles(incoming: File[], input: HTMLInputElement) {
    this.error.set('');
    this.success.set('');

    if (!incoming.length) {
      this.file.set(null);
      this.extraFiles.set([]);
      return;
    }

    const valid: File[] = [];
    for (const item of incoming) {
      if (!/\.(pdf|docx|txt)$/i.test(item.name) || item.size === 0 || item.size > 10_485_760) {
        this.error.set(
          `«${item.name}» no es válido. Selecciona archivos PDF, DOCX o TXT no vacíos de hasta 10 MiB.`,
        );
        this.showMessage();
        input.value = '';
        if (!this.file()) {
          this.file.set(null);
          this.extraFiles.set([]);
        }
        return;
      }
      valid.push(item);
    }

    if (this.previousVersionId) {
      const first = valid[0];
      this.file.set(first);
      this.extraFiles.set([]);
      if (!this.title) this.title = first.name.replace(/\.[^.]+$/, '').slice(0, 160);
      return;
    }

    // No descartar archivos distintos solo por coincidir su nombre y tamaño.
    const existing = this.selectedFiles();
    const merged = [...existing];
    for (const item of valid) {
      if (!merged.includes(item)) {
        merged.push(item);
      }
    }
    this.file.set(merged[0] ?? null);
    this.extraFiles.set(merged.slice(1));
    if (!this.title && merged[0]) {
      this.title = merged[0].name.replace(/\.[^.]+$/, '').slice(0, 160);
    }
    input.value = '';
  }

  removeFile(input: HTMLInputElement, index = 0) {
    const current = this.selectedFiles();
    if (index <= 0 && current.length <= 1) {
      this.file.set(null);
      this.extraFiles.set([]);
      input.value = '';
      return;
    }
    const next = current.filter((_, idx) => idx !== index);
    this.file.set(next[0] ?? null);
    this.extraFiles.set(next.slice(1));
    if (index === 0 && next[0]) {
      this.title = next[0].name.replace(/\.[^.]+$/, '').slice(0, 160);
    }
    input.value = '';
  }

  clearAllFiles(input: HTMLInputElement) {
    this.file.set(null);
    this.extraFiles.set([]);
    input.value = '';
  }

  fileType(file: File) {
    return file.name.split('.').pop()?.toUpperCase() ?? 'FILE';
  }

  // Envío de uno o varios archivos al backend para la misma asignatura
  upload(input: HTMLInputElement) {
    const file = this.file();
    const extras = this.extraFiles();
    const baseTitle = this.title.trim();
    if (!file || (!baseTitle && !extras.length) || !this.metadataReady() || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    const meta = {
      course: this.course.trim(),
      source_reference: this.sourceReference.trim(),
      permission_note: this.permissionNote.trim(),
      authorization_confirmed: this.authorizationConfirmed,
      previous_version_id: this.previousVersionId,
    };

    if (extras.length === 0) {
      this.service
        .upload(file, baseTitle, meta)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: (saved) => {
            this.busy.set(false);
            this.file.set(null);
            this.extraFiles.set([]);
            this.title = '';
            this.previousVersionId = undefined;
            this.authorizationConfirmed = false;
            input.value = '';
            this.success.set(
              'Documento guardado. Abre sus detalles para extraer y segmentar el texto.',
            );
            this.load(0);
            this.loadCourseOptions();
            if (this.autoPrepareOnUpload) {
              this.detailRequest?.unsubscribe();
              this.detailLoading.set(false);
              this.openPanel('detail');
              this.detailSection.set('content');
              this.selectedChunk.set(null);
              this.selected.set(saved);
              this.prepareForReview(saved);
            } else {
              this.view(saved);
            }
          },
          error: (error) => {
            this.error.set(this.message(error));
            this.showMessage();
            this.busy.set(false);
          },
        });
      return;
    }

    const queue = [file, ...extras];
    const failed: File[] = [];
    const failures: string[] = [];
    from(queue.map((item, idx) => ({ item, idx })))
      .pipe(
        concatMap(({ item, idx }) => {
          const derivedTitle =
            idx === 0 && baseTitle
              ? baseTitle
              : item.name.replace(/\.[^.]+$/, '').slice(0, 160) || `Documento ${idx + 1}`;
          return this.service.upload(item, derivedTitle, {
            ...meta,
            previous_version_id: undefined,
          }).pipe(catchError((error: HttpErrorResponse) => {
            failed.push(item);
            failures.push(`«${item.name}»: ${this.message(error)}`);
            return of(null);
          }));
        }),
        toArray(),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (results) => {
          const savedList = results.filter((item): item is CourseDocument => item !== null);
          this.busy.set(false);
          if (failed.length) {
            this.file.set(failed[0]);
            this.extraFiles.set(failed.slice(1));
            this.title = failed[0].name.replace(/\.[^.]+$/, '').slice(0, 160);
            input.value = '';
            this.load(0);
            this.loadCourseOptions();
            this.success.set(`${savedList.length} documentos guardados. Prepara los guardados desde la biblioteca.`);
            this.error.set(`${failures.join(' ')} Solo quedan seleccionados los archivos que fallaron.`);
            this.showMessage();
            return;
          }
          this.file.set(null);
          this.extraFiles.set([]);
          this.title = '';
          this.previousVersionId = undefined;
          this.authorizationConfirmed = false;
          input.value = '';
          if (this.autoPrepareOnUpload) {
            this.prepareBatch(savedList, meta.course);
            return;
          }
          this.success.set(
            `Se guardaron ${savedList.length} documentos en «${meta.course}». Puedes procesarlos desde la biblioteca.`,
          );
          this.load(0);
          this.loadCourseOptions();
          if (savedList.length === 1) {
            this.view(savedList[0]);
          } else {
            this.closePanel();
            this.showMessage();
          }
        },
        error: (error) => {
          this.error.set(this.message(error));
          this.showMessage();
          this.busy.set(false);
          this.load(0);
          this.loadCourseOptions();
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
    this.publicationReviewed.set(false);
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
    this.publicationReviewed.set(false);
    this.selected.set(null);
  }

  // Etapa 1: Extracción y segmentación de texto
  process(rebuild = false) {
    const document = this.selected();
    if (
      !document ||
      this.locked() ||
      (document.processing_status === 'processed' && !rebuild) ||
      (rebuild && (!!document.published_at || document.index_status === 'indexing')) ||
      (document.processing_status === 'processing' && !this.canRetryProcessing(document))
    )
      return;
    this.reviewingFragments.set(false);
    this.selectedChunk.set(null);
    this.processingId.set(document.id);
    this.error.set('');
    this.success.set('');
    this.service
      .process(document.id, rebuild)
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
    if (publish && !this.publicationReviewed()) return;
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
          this.loadCourseOptions();
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

  // Preparación automática: extraer e indexar; la publicación requiere revisión.
  private ensurePrepared$(document: CourseDocument): Observable<CourseDocument> {
    const step1$: Observable<CourseDocument> =
      document.processing_status === 'processed'
        ? of(document)
        : this.service.process(document.id).pipe(tap((item) => this.updateDocument(item)));

    return step1$.pipe(
      switchMap((processed) =>
        processed.index_status === 'indexed'
          ? of(processed)
          : this.service.index(processed.id, false).pipe(tap((item) => this.updateDocument(item))),
      ),
    );
  }

  prepareForReview(target?: CourseDocument | null) {
    const document = target ?? this.selected();
    if (!document || this.locked() || document.published_at) return;
    this.autoPreparing.set(true);
    this.error.set('');
    this.success.set('');
    this.ensurePrepared$(document)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this.autoPreparing.set(false);
          this.updateDocument(item);
          this.loadCourseOptions();
          this.reviewingFragments.set(true);
          this.success.set(
            `«${item.title}»: listo para revisar. Comprueba los fragmentos y habilita la fuente cuando estén correctos.`,
          );
          this.showMessage();
        },
        error: (error) => {
          this.autoPreparing.set(false);
          this.error.set(this.message(error));
          this.showMessage();
        },
      });
  }

  prepareAllPending() {
    const list = this.pendingDocuments();
    if (!list.length || this.locked()) return;
    this.prepareBatch(list);
  }

  private prepareBatch(list: CourseDocument[], courseName?: string) {
    this.autoPreparing.set(true);
    this.error.set('');
    this.success.set('');
    const failures: string[] = [];
    from(list)
      .pipe(
        concatMap((doc) => this.ensurePrepared$(doc).pipe(
          map(() => true),
          catchError((error: HttpErrorResponse) => {
            failures.push(`«${doc.title}»: ${this.message(error)}`);
            return of(false);
          }),
        )),
        toArray(),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (enabledList) => {
          this.autoPreparing.set(false);
          this.load(this.offset());
          this.loadCourseOptions();
          if (courseName) this.closePanel();
          if (failures.length) this.error.set(failures.join(' '));
          this.success.set(
            `Preparados para revisión: ${enabledList.filter(Boolean).length} de ${list.length}. Revisa y habilita cada fuente desde su detalle.`,
          );
          this.showMessage();
        },
        error: (error) => {
          this.autoPreparing.set(false);
          this.load(this.offset());
          this.loadCourseOptions();
          this.error.set(this.message(error));
          this.showMessage();
        },
      });
  }

  // Actualización en memoria y borrado
  private updateDocument(document: CourseDocument) {
    this.publicationReviewed.set(false);
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
          this.loadCourseOptions();
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
