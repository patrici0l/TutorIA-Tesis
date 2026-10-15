import { Component, DestroyRef, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import {
  Assignment,
  AssignmentStatus,
  ASSIGNMENT_STATUS_LABELS,
  AssignmentPage,
  AssignmentService,
  AssignmentSubmission,
} from '../../servicios/assignment.service';
import { PRACTICE_BANKS } from '../../modelos/practice-bank';

@Component({
  selector: 'app-assignments',
  imports: [FormsModule, DatePipe, RouterLink],
  templateUrl: './assignments.component.html',
  styleUrl: './assignments.component.scss',
})
export class AssignmentsComponent implements OnInit {
  readonly auth = inject(AuthService);
  private readonly service = inject(AssignmentService);
  private readonly destroy = inject(DestroyRef);
  readonly teacher = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly banks = PRACTICE_BANKS;
  readonly page = signal<AssignmentPage | null>(null);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly formError = signal('');
  readonly success = signal('');
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  readonly pendingChange = signal<{ item: Assignment; status: AssignmentStatus } | null>(null);
  readonly changing = signal(false);
  readonly statusError = signal('');
  readonly statusSuccess = signal('');
  title = '';
  email = '';
  instructions = '';
  version = 'derivadas-v1';
  private submission: AssignmentSubmission | null = null;
  ngOnInit() {
    this.load();
  }
  bankTitle(version: string) {
    return this.banks.find((b) => b.version === version)?.title ?? 'Práctica anterior';
  }
  load(offset = 0) {
    if (this.loading() || this.changing() || this.saving()) return;
    this.pendingChange.set(null);
    this.loading.set(true);
    this.error.set('');
    this.service
      .list(offset)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (page) => {
          this.page.set(page);
          this.loading.set(false);
        },
        error: () => {
          this.error.set('No pudimos cargar las actividades. Vuelve a intentarlo.');
          this.loading.set(false);
        },
      });
  }
  create() {
    if (!this.teacher() || this.saving() || this.changing() || this.loading()) return;
    const data = {
      student_email: this.email.trim().toLowerCase(),
      title: this.title.trim(),
      instructions: this.instructions.trim(),
      version: this.version,
    };
    if (!data.title || !data.student_email) {
      this.formError.set('Completa el título y el correo del estudiante.');
      return;
    }
    if (
      !this.submission ||
      Object.entries(data).some(([k, v]) => this.submission![k as keyof AssignmentSubmission] !== v)
    )
      this.submission = { id: crypto.randomUUID(), ...data };
    this.saving.set(true);
    this.formError.set('');
    this.success.set('');
    this.service
      .create(this.submission)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.submission = null;
          this.title = '';
          this.instructions = '';
          this.success.set('Actividad asignada. El estudiante ya puede verla.');
          this.load();
        },
        error: (error) => {
          this.saving.set(false);
          this.formError.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No pudimos confirmar la asignación. Reintenta sin cambiar los datos para evitar duplicados.',
          );
        },
      });
  }
  requestStatus(item: Assignment, status: AssignmentStatus) {
    if (!this.teacher() || this.changing() || this.saving() || this.loading()) return;
    this.statusError.set('');
    this.statusSuccess.set('');
    this.pendingChange.set({ item, status });
  }
  confirmStatus() {
    const change = this.pendingChange();
    if (!change || !this.teacher() || this.changing() || this.saving() || this.loading()) return;
    this.changing.set(true);
    this.statusError.set('');
    this.service
      .changeStatus(change.item, change.status)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (updated) => {
          this.page.update((page) =>
            page
              ? {
                  ...page,
                  items: page.items.map((item) => (item.id === updated.id ? updated : item)),
                }
              : page,
          );
          this.changing.set(false);
          this.pendingChange.set(null);
          this.statusSuccess.set(
            `Actividad «${updated.title}»: ${this.statusLabels[updated.status].toLowerCase()}.`,
          );
        },
        error: (error) => {
          this.changing.set(false);
          this.statusError.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No pudimos confirmar el cambio. Puedes reintentarlo o actualizar el listado.',
          );
        },
      });
  }
}
