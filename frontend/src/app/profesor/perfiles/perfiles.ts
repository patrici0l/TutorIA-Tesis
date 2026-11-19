// Registra y consulta observaciones sintéticas privadas para la adaptación opcional.
import { Component, DestroyRef, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../inicio/sesion.service';
import {
  MasteryLevel,
  RecommendedSupport,
  ProfilePage,
  ProfileRequest,
  ProfileResponse,
} from './perfiles.model';
import { ProfileService } from './perfiles.service';
import { RouterLink } from '@angular/router';
import { ViewAttention } from '../../compartido/atencion-vista.service';

@Component({
  selector: 'app-performance-profiles',
  imports: [FormsModule, DatePipe, RouterLink],
  templateUrl: './perfiles.html',
  styleUrl: './perfiles.scss',
})
export class ProfilesComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly service = inject(ProfileService);
  private readonly destroy = inject(DestroyRef);
  private readonly attention = inject(ViewAttention);
  readonly allowed = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly busy = signal(false);
  readonly error = signal('');
  readonly fieldErrors = signal<Record<string, string>>({});
  readonly submitted = signal(false);
  readonly selected = signal<ProfileResponse | null>(null);
  readonly page = signal<ProfilePage | null>(null);
  readonly masteryLabels = { low: 'Bajo', medium: 'Medio', high: 'Alto' };
  readonly supportLabels = {
    reinforcement: 'Refuerzo',
    practice: 'Práctica guiada',
    challenge: 'Retos',
  };
  readonly trendLabels = { improving: 'Mejora', stable: 'Estable', declining: 'Descenso' };
  studentId = '';
  topic = '';
  performance: number | null = null;
  attempts: number | null = null;
  errorsText = '';
  mastery: MasteryLevel = 'low';
  support: RecommendedSupport = 'reinforcement';
  resolutionTime: number | null = null;
  trend: '' | 'improving' | 'stable' | 'declining' = '';
  confirmed = false;
  ngOnInit() {
    if (this.allowed()) this.load();
  }
  fieldError(field: string) {
    return this.fieldErrors()[field] ?? '';
  }
  validateAfterEdit() {
    if (this.submitted()) {
      const errors = this.validationErrors();
      this.fieldErrors.set(errors);
      if (!Object.keys(errors).length && this.error().startsWith('Revisa los campos señalados')) this.error.set('');
    }
  }
  private validationErrors() {
    const errors: Record<string, string> = {};
    if (!this.studentId.trim()) errors['studentId'] = 'Indica un identificador ficticio.';
    else if (!/^[A-Za-z0-9_-]{1,64}$/.test(this.studentId.trim())) errors['studentId'] = 'Usa hasta 64 letras sin tildes, números, guiones o guiones bajos.';
    if (!this.topic.trim()) errors['profileTopic'] = 'Indica el tema de esta observación.';
    else if (this.topic.trim().length > 160) errors['profileTopic'] = 'El tema admite hasta 160 caracteres.';
    if (this.performance === null || !Number.isFinite(this.performance) || this.performance < 0 || this.performance > 100) errors['performance'] = 'Indica un desempeño entre 0 y 100 %.';
    if (this.attempts === null || !Number.isInteger(this.attempts) || this.attempts < 1 || this.attempts > 10000) errors['attempts'] = 'Indica un número entero de intentos entre 1 y 10 000.';
    const labels = this.errorsText.split(/\r?\n/).map(value => value.trim()).filter(Boolean);
    if (labels.length > 10) errors['frequentErrors'] = 'Usa como máximo diez etiquetas, una por línea.';
    else if (new Set(labels).size !== labels.length) errors['frequentErrors'] = 'Hay etiquetas repetidas. Conserva una sola línea para cada error frecuente.';
    else if (labels.some(value => value.length > 100)) errors['frequentErrors'] = 'Cada etiqueta admite como máximo 100 caracteres.';
    if (this.resolutionTime !== null && (!Number.isFinite(this.resolutionTime) || this.resolutionTime < 0 || this.resolutionTime > 86400)) errors['time'] = 'Indica un tiempo entre 0 y 86 400 segundos o deja el campo vacío.';
    if (!this.confirmed) errors['profile-confirmed'] = 'Confirma que la observación contiene únicamente datos ficticios.';
    return errors;
  }
  save() {
    if (!this.allowed() || this.busy()) return;
    this.submitted.set(true);
    const fieldErrors = this.validationErrors();
    this.fieldErrors.set(fieldErrors);
    if (Object.keys(fieldErrors).length) {
      this.error.set('Revisa los campos señalados antes de guardar. Tus datos se conservan.');
      this.attention.reveal(Object.keys(fieldErrors)[0]);
      return;
    }
    const errors = this.errorsText
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);
    const request: ProfileRequest = {
      student_id: this.studentId.trim(),
      topic: this.topic.trim(),
      performance: this.performance!,
      attempts: this.attempts!,
      frequent_errors: errors,
      mastery_level: this.mastery,
      recommended_support: this.support,
      data_kind: 'synthetic',
    };
    if (this.resolutionTime !== null) request.resolution_time_seconds = this.resolutionTime;
    if (this.trend) request.progress_trend = this.trend;
    this.busy.set(true);
    this.error.set('');
    this.service
      .create(request)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (record) => {
          this.selected.set(record);
          this.fieldErrors.set({});
          this.submitted.set(false);
          this.busy.set(false);
          this.load();
        },
        error: () => {
          this.busy.set(false);
          this.error.set(
            'No se pudo confirmar el guardado. Consulta la lista antes de volver a enviar.',
          );
        },
      });
  }
  load(offset = 0) {
    if (!this.allowed() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.service
      .page(offset)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (page) => {
          this.page.set(page);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('No se pudo consultar la lista. Inténtalo nuevamente.');
          this.busy.set(false);
        },
      });
  }
  open(id: string) {
    if (!this.allowed() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.service
      .detail(id)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (record) => {
          this.selected.set(record);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('Perfil no disponible. Actualiza la lista.');
          this.busy.set(false);
        },
      });
  }
}
