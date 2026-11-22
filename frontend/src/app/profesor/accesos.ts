import { Component, DestroyRef, inject, signal } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize } from 'rxjs';
import { AuthService } from '../inicio/sesion.service';
import { CourseCatalogService, CourseOption } from './documentos/asignaturas.service';

interface LearningAccess { id: string; course: string; student_email: string; active: boolean }

@Component({
  selector: 'app-learning-access', imports: [FormsModule],
  styleUrl: './accesos.scss',
  template: `
    <header class="page-heading"><h1>Acceso de estudiantes</h1><p>Permite que un estudiante solicite contenido con tus materiales habilitados de una asignatura.</p></header>
    @if (!canManage()) { <p>Solo el profesor puede gestionar estos accesos.</p> } @else {
      @if (error()) { <p role="alert" class="notice error">{{ error() }}</p> }
      @if (message()) { <p role="status">{{ message() }}</p> }
      <section class="panel"><h2>Habilitar una asignatura</h2>
        <p>El estudiante debe haber iniciado sesión al menos una vez. Podrá consultar los fragmentos habilitados de esta materia, incluidos los que habilites después.</p>
        <form (ngSubmit)="grant()"><fieldset [disabled]="busy()">
          <legend class="sr-only">Dar acceso</legend>
          <label for="access-email">Correo del estudiante</label><input id="access-email" name="email" type="email" [(ngModel)]="email" required maxlength="254" />
          <label for="access-course">Asignatura</label><select id="access-course" name="course" [(ngModel)]="course" required><option value="">Selecciona una asignatura</option>@for (c of courses(); track c.value) { <option [value]="c.value">{{ c.label }} · {{ c.enabled }} materiales habilitados</option> }</select>
          <p class="help">Dar acceso no publica documentos. Debes procesarlos, preparar su búsqueda y habilitarlos desde Mis documentos.</p>
          <button type="submit" class="primary" [disabled]="!email.trim() || !course">Dar acceso</button>
        </fieldset></form>
      </section>
      <section class="panel"><h2>Accesos concedidos</h2><button (click)="load()" [disabled]="busy()">Actualizar</button>
        <p>Retirar el acceso impide nuevas solicitudes y el envío de preparaciones pendientes. El estudiante conserva el contenido ya guardado en su historial.</p>
        @if (!accesses().length) { <p>Todavía no hay accesos registrados.</p> }
        <ul class="history-list">@for (a of accesses(); track a.id) {
          <li><div><strong>{{ a.course }}</strong><p>{{ a.student_email }} · {{ a.active ? 'Activo' : 'Retirado' }}</p></div>
            @if (a.active) { <button (click)="pending.set(a)" [disabled]="busy()">Retirar acceso<span class="sr-only"> de {{ a.student_email }} a {{ a.course }}</span></button> }
          </li>
        }</ul>
        @if (pending(); as a) { <div role="group" aria-label="Confirmar retirada"><p>¿Retirar el acceso de {{ a.student_email }} a {{ a.course }}?</p><div class="actions"><button (click)="revoke(a)" [disabled]="busy()">Sí, retirar</button><button (click)="pending.set(null)" [disabled]="busy()">Cancelar</button></div></div> }
      </section>
    }
  `,
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
  readonly error = signal('');
  readonly message = signal('');
  email = ''; course = '';
  canManage() { return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''); }
  constructor() { if (this.canManage()) this.load(); }
  load() {
    this.error.set('');
    this.catalog.load().pipe(takeUntilDestroyed(this.destroy)).subscribe({ next: c => this.courses.set(c), error: e => this.fail(e) });
    this.http.get<LearningAccess[]>('/api/v1/learning/access').pipe(takeUntilDestroyed(this.destroy))
      .subscribe({ next: a => this.accesses.set(a), error: e => this.fail(e) });
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
