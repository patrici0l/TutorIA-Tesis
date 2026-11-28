import { Component, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize } from 'rxjs';
import { AuthService } from '../../inicio/sesion.service';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { CourseCatalogService, CourseOption } from './asignaturas.service';
import { CorePreview, CoreResult } from './fuentes-externas.model';
import { CourseDocument } from './documentos.model';

@Component({
  selector: 'app-core-sources', imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './fuentes-core.html', styleUrls: ['./fuentes-externas.scss', './fuentes-core.scss'],
})
export class CoreSourcesComponent {
  readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly destroy = inject(DestroyRef);
  private readonly attention = inject(ViewAttention);
  private readonly catalog = inject(CourseCatalogService);
  readonly courses = signal<CourseOption[]>([]);
  readonly results = signal<CoreResult[]>([]);
  readonly preview = signal<CorePreview | null>(null);
  readonly imported = signal<CourseDocument | null>(null);
  readonly busy = signal(false);
  readonly status = signal('');
  readonly error = signal('');
  readonly searched = signal(false);
  readonly file = signal<File | null>(null);
  query = ''; course = ''; permission = ''; confirmed = false;
  private readonly base = '/api/v1/documents/external/core';
  canManage() { return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''); }
  constructor() {
    if (this.canManage()) this.catalog.load().pipe(takeUntilDestroyed(this.destroy)).subscribe({
      next: rows => this.courses.set(rows), error: () => {},
    });
  }
  search() {
    if (this.busy() || !this.canManage()) return;
    if (this.query.trim().length < 2) { this.fail('Escribe un tema de al menos dos caracteres.'); return; }
    this.preview.set(null); this.imported.set(null); this.results.set([]); this.searched.set(false);
    this.begin('Buscando publicaciones en CORE…');
    this.http.get<CoreResult[]>(this.base + '/search', { params: { q: this.query.trim() } })
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.busy.set(false)))
      .subscribe({ next: rows => { this.results.set(rows); this.searched.set(true); this.attention.reveal('core-results'); }, error: e => this.fail(this.message(e)) });
  }
  review(row: CoreResult) {
    if (this.busy() || !this.canManage()) return;
    this.preview.set(null); this.imported.set(null); this.file.set(null); this.permission = ''; this.confirmed = false;
    this.begin('Consultando la ficha y la disponibilidad del texto…');
    this.http.get<CorePreview>(this.base + '/preview/' + row.work_id)
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.busy.set(false)))
      .subscribe({ next: p => { this.preview.set(p); this.attention.reveal('core-preview'); }, error: e => this.fail(this.message(e)) });
  }
  chooseFile(event: Event) {
    this.confirmed = false;
    const f = (event.target as HTMLInputElement).files?.[0];
    this.file.set(null);
    if (!f) return;
    if (!/\.(pdf|docx|txt)$/i.test(f.name) || f.size > 10 * 1024 * 1024 || !f.size) {
      this.fail('Elige un PDF con texto, DOCX o TXT de hasta 10 MB.'); return;
    }
    this.error.set(''); this.file.set(f);
  }
  importOriginal() {
    const p = this.preview(), f = this.file();
    if (this.busy() || !this.canManage() || !p || !f || this.imported()) return;
    if (!this.course.trim() || this.permission.trim().length < 10 || !this.confirmed) {
      this.fail('Indica la asignatura, el permiso de uso y confirma la revisión del original.'); return;
    }
    const body = new FormData();
    body.set('file', f); body.set('work_id', String(p.work_id)); body.set('record_sha256', p.record_sha256);
    body.set('course', this.course.trim()); body.set('permission_note', this.permission.trim()); body.set('authorization_confirmed', 'true');
    this.begin('Guardando el original y la ficha de CORE…');
    this.http.post<CourseDocument>(this.base + '/import', body)
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.busy.set(false)))
      .subscribe({ next: doc => { this.imported.set(doc); this.attention.reveal('core-success'); }, error: e => this.fail(this.message(e)) });
  }
  private begin(text: string) { this.status.set(text); this.error.set(''); this.busy.set(true); }
  private fail(text: string) { this.error.set(text); this.attention.reveal('core-error'); }
  private message(e: HttpErrorResponse) { return typeof e.error?.detail === 'string' ? e.error.detail : 'No se pudo completar la operación. Revisa los datos e inténtalo de nuevo.'; }
}
