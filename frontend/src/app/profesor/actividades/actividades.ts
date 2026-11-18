import { NgSelectComponent, NgOptionTemplateDirective } from '@ng-select/ng-select';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { AssignmentCardComponent } from '../../compartido/actividades/tarjeta';
import { AssignmentListState } from '../../compartido/actividades/lista-actividades.state';
// Gestiona asignaciones docentes y distingue bancos corregibles de material de estudio.
import { Component, DestroyRef, computed, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { PreparationService } from '../recursos/recursos.service';
import { HistoryDetail } from '../recursos/historial.model';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../inicio/sesion.service';
import { AssignmentService } from '../../compartido/actividades/actividades.service';
import {
  Assignment,
  AssignmentStatus,
  ASSIGNMENT_STATUS_LABELS,
  AssignmentSubmission,
} from '../../compartido/actividades/actividades.model';
import { PRACTICE_BANKS } from '../../compartido/practica/bancos';

@Component({
  selector: 'app-teacher-assignments',
  imports: [
    NgSelectComponent,
    NgOptionTemplateDirective,
    DatePipe,
    FormsModule,
    RouterLink,
    AssignmentCardComponent,
  ],
  providers: [AssignmentListState],
  templateUrl: './actividades.html',
  styleUrls: ['./actividades.scss', './seguimiento.scss'],
})
export class TeacherAssignmentsComponent implements OnInit {
  private readonly attention = inject(ViewAttention);
  readonly auth = inject(AuthService);
  private readonly service = inject(AssignmentService);
  private readonly route = inject(ActivatedRoute);
  private readonly resources = inject(PreparationService);
  readonly selectedResource = signal<HistoryDetail | null>(null);
  readonly resourceLoading = signal(false);
  readonly resourceError = signal('');
  private readonly destroy = inject(DestroyRef);
  readonly teacher = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly contentOptions = computed(() => [
    ...(this.selectedResource()
      ? [
          {
            value: 'resource-v1',
            label: this.selectedResource()!.resource!.title,
            kind:
              this.selectedResource()!.resource!.resource_type === 'QUIZ'
                ? 'Quiz interactivo · autoevaluación'
                : 'Material de estudio',
          },
        ]
      : []),
    ...PRACTICE_BANKS.map((bank) => ({
      value: bank.version,
      label: bank.title,
      kind: 'Ejercicios autocorregidos · resultado guardado',
    })),
  ]);
  readonly banks = PRACTICE_BANKS;
  private readonly listing = inject(AssignmentListState);
  readonly page = this.listing.page;
  readonly loading = this.listing.loading;
  readonly saving = signal(false);
  readonly error = this.listing.error;
  readonly formError = signal('');
  readonly success = signal('');
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  readonly pendingChange = signal<{ item: Assignment; status: AssignmentStatus } | null>(null);
  readonly changing = signal(false);
  readonly statusError = signal('');
  readonly statusSuccess = signal('');
  readonly activeView = signal<'assign' | 'tracking'>('assign');
  readonly search = signal('');
  readonly statusFilter = signal('');
  readonly typeFilter = signal('');
  readonly selectedId = signal<string | null>(null);
  readonly detailTab = signal<'overview' | 'results'>('overview');
  readonly filtered = computed(() =>
    (this.page()?.items ?? []).filter(
      (item) =>
        (!this.statusFilter() || item.status === this.statusFilter()) &&
        (!this.typeFilter() || (this.typeFilter() === 'resource') === !!item.resource_id) &&
        `${item.title} ${item.student_email}`
          .toLocaleLowerCase()
          .includes(this.search().trim().toLocaleLowerCase()),
    ),
  );
  selectActivity(id: string) {
    this.selectedId.set(this.selectedId() === id ? null : id);
    this.detailTab.set('overview');
    this.pendingChange.set(null);
  }
  title = '';
  email = '';
  instructions = '';
  version = 'derivadas-v1';
  private submission: AssignmentSubmission | null = null;
  ngOnInit() {
    this.load();
    const id = this.route.snapshot.queryParamMap.get('resource');
    if (id && this.teacher()) {
      this.version = 'resource-v1';
      this.resourceLoading.set(true);
      this.resources
        .detail(id)
        .pipe(takeUntilDestroyed(this.destroy))
        .subscribe({
          next: (detail) => {
            this.resourceLoading.set(false);
            if (detail.status !== 'succeeded' || !detail.resource) {
              this.resourceError.set('Genera el recurso correctamente antes de asignarlo.');
              this.attention.reveal('assignment-resource-error');
              return;
            }
            this.selectedResource.set(detail);
            this.title = detail.resource.title.slice(0, 120);
            this.attention.reveal('assignment-recipient-title');
          },
          error: () => {
            this.resourceLoading.set(false);
            this.resourceError.set(
              'No pudimos abrir el recurso. Vuelve a Mis recursos para seleccionarlo.',
            );
            this.attention.reveal('assignment-resource-error');
          },
        });
    }
  }
  load(offset = 0) {
    if (this.loading() || this.changing() || this.saving()) return;
    this.pendingChange.set(null);
    this.selectedId.set(null);
    this.listing.load(offset);
  }
  create() {
    if (!this.teacher() || this.saving() || this.changing() || this.loading()) return;
    if (this.resourceLoading() || (this.version === 'resource-v1' && !this.selectedResource()))
      return;
    const data = {
      student_email: this.email.trim().toLowerCase(),
      title: this.title.trim(),
      instructions: this.instructions.trim(),
      version: this.version,
      ...(this.version === 'resource-v1'
        ? { resource_id: this.selectedResource()!.preparation.id }
        : {}),
    };
    if (!data.title || !data.student_email) {
      this.formError.set('Completa el título y el correo del estudiante.');
      this.attention.reveal('assignment-form-error');
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
          this.attention.reveal('assignment-success');
          this.load();
        },
        error: (error) => {
          this.saving.set(false);
          this.formError.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No pudimos confirmar la asignación. Reintenta sin cambiar los datos para evitar duplicados.',
          );
          this.attention.reveal('assignment-form-error');
        },
      });
  }
  requestStatus(item: Assignment, status: AssignmentStatus) {
    if (!this.teacher() || this.changing() || this.saving() || this.loading()) return;
    this.statusError.set('');
    this.statusSuccess.set('');
    this.pendingChange.set({ item, status });
    this.attention.reveal('change-' + item.id);
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
