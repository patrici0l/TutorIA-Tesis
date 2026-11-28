import { Component, DestroyRef, inject, signal, computed } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize, forkJoin } from 'rxjs';
import { AuthService } from '../inicio/sesion.service';
import { CourseCatalogService, CourseOption } from './documentos/asignaturas.service';

interface LearningAccess { id: string; course: string; student_email: string; active: boolean }

@Component({
  selector: 'app-learning-access', imports: [FormsModule],
  styleUrl: './accesos.scss',
  templateUrl: './accesos.html',
})
export class LearningAccessComponent {
  private readonly http = inject(HttpClient);
  private readonly catalog = inject(CourseCatalogService);
  private readonly destroy = inject(DestroyRef);
  readonly auth = inject(AuthService);
  readonly courses = signal<CourseOption[]>([]);
  readonly accesses = signal<LearningAccess[]>([]);
  readonly pending = signal<LearningAccess | null>(null);
  readonly busy = signal(false);
  readonly loading = signal(false);
  readonly loaded = signal(false);
  readonly filter = signal('active');
  readonly search = signal('');
  readonly activeCount = computed(() => this.accesses().filter(a => a.active).length);
  readonly visible = computed(() => this.accesses().filter(a => (this.filter() === 'all' || (this.filter() === 'active' ? a.active : !a.active)) && (a.course + ' ' + a.student_email).toLowerCase().includes(this.search().trim().toLowerCase())));
  selectedCourse() { return this.courses().find(c => c.value === this.course); }
  readonly error = signal('');
  readonly message = signal('');
  email = ''; course = '';
  canManage() { return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''); }
  constructor() { if (this.canManage()) this.load(); }
  load() {
    if (this.loading()) return;
    this.error.set(''); this.loading.set(true);
    forkJoin({ courses: this.catalog.load(), accesses: this.http.get<LearningAccess[]>('/api/v1/learning/access') })
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.loading.set(false)))
      .subscribe({ next: data => { this.courses.set(data.courses); this.accesses.set(data.accesses); this.loaded.set(true); }, error: e => this.fail(e) });
  }
  grant() {
    if (this.busy() || !this.email.trim() || !this.course) return;
    this.busy.set(true); this.error.set(''); this.message.set('');
    this.http.post('/api/v1/learning/access', { student_email: this.email.trim(), course: this.course })
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.busy.set(false)))
      .subscribe({ next: () => { this.message.set('Acceso habilitado. El estudiante ya puede entrar en Solicitar contenido.'); this.load(); }, error: e => this.fail(e) });
  }
  revoke(access: LearningAccess) {
    if (this.busy()) return;
    this.busy.set(true); this.error.set(''); this.message.set('');
    this.http.delete('/api/v1/learning/access/' + access.id)
      .pipe(takeUntilDestroyed(this.destroy), finalize(() => this.busy.set(false)))
      .subscribe({ next: () => { this.pending.set(null); this.message.set('Acceso retirado.'); this.load(); }, error: e => this.fail(e) });
  }
  private fail(e: HttpErrorResponse) { this.error.set(typeof e.error?.detail === 'string' ? e.error.detail : 'No se pudo completar la operación. Actualiza y vuelve a intentarlo.'); }
}
