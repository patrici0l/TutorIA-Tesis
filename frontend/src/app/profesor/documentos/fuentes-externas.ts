import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize } from 'rxjs';
import { AuthService } from '../../inicio/sesion.service';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { WikiPreview, WikiResult } from './fuentes-externas.model';
import { CourseDocument } from './documentos.model';

@Component({
  selector: 'app-external-sources',
  imports: [FormsModule, RouterLink, DatePipe],
  templateUrl: './fuentes-externas.html',
  styleUrl: './fuentes-externas.scss',
})
export class ExternalSourcesComponent {
  private readonly http = inject(HttpClient);
  private readonly destroyRef = inject(DestroyRef);
  private readonly attention = inject(ViewAttention);
  readonly auth = inject(AuthService);
  readonly canManage = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly busy = signal(false);
  readonly error = signal('');
  readonly results = signal<WikiResult[]>([]);
  readonly searched = signal(false);
  readonly preview = signal<WikiPreview | null>(null);
  readonly imported = signal<CourseDocument | null>(null);
  query = '';
  course = '';
  confirmed = false;
  private readonly base = '/api/v1/documents/external/wikipedia';

  search() {
    if (this.busy() || !this.canManage()) return;
    if (this.query.trim().length < 2) { this.fail('Escribe un tema de al menos dos caracteres.'); return; }
    this.error.set(''); this.preview.set(null); this.imported.set(null);
    this.confirmed = false; this.results.set([]); this.searched.set(false); this.busy.set(true);
    this.http.get<WikiResult[]>(this.base + '/search', { params: { q: this.query.trim() } })
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.busy.set(false)))
      .subscribe({ next: (rows) => {
        this.results.set(rows); this.searched.set(true); this.attention.reveal('external-results');
      }, error: (e) => this.fail(this.message(e)) });
  }
  review(item: WikiResult) {
    if (this.busy() || !this.canManage()) return;
    this.busy.set(true); this.error.set(''); this.preview.set(null);
    this.imported.set(null); this.confirmed = false;
    this.http.get<WikiPreview>(this.base + '/preview/' + item.page_id)
      .pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.busy.set(false)))
      .subscribe({ next: (value) => {
        this.preview.set(value); this.attention.reveal('external-preview');
      }, error: (e) => this.fail(this.message(e)) });
  }
  importArticle() {
    const preview = this.preview();
    if (this.busy() || !this.canManage() || !preview || this.imported()) return;
    if (!this.course.trim() || !this.confirmed) {
      this.fail('Indica la asignatura y confirma la revisión de la fuente y su licencia.'); return;
    }
    this.busy.set(true); this.error.set('');
    this.http.post<CourseDocument>(this.base + '/import', {
      page_id: preview.source.page_id, revision_id: preview.source.revision_id,
      text_sha256: preview.source.text_sha256, course: this.course.trim(),
      authorization_confirmed: true,
    }).pipe(takeUntilDestroyed(this.destroyRef), finalize(() => this.busy.set(false)))
      .subscribe({ next: (document) => {
        this.imported.set(document); this.attention.reveal('external-success');
      }, error: (e) => this.fail(this.message(e)) });
  }
  private fail(message: string) { this.error.set(message); this.attention.reveal('external-error'); }
  private message(error: HttpErrorResponse): string {
    return typeof error.error?.detail === 'string' ? error.error.detail
      : 'No se pudo completar la consulta. Revisa los datos e inténtalo de nuevo.';
  }
}
