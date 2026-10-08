import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import {
  MasteryLevel,
  RecommendedSupport,
  ProfilePage,
  ProfileRequest,
  ProfileResponse,
} from '../../modelos/profile.model';
import { ProfileService } from '../../servicios/profile.service';

@Component({
  selector: 'app-performance-profiles',
  imports: [FormsModule, DatePipe],
  templateUrl: './profiles.component.html',
  styleUrl: './profiles.component.scss',
})
export class ProfilesComponent {
  private readonly auth = inject(AuthService);
  private readonly service = inject(ProfileService);
  private readonly destroy = inject(DestroyRef);
  readonly allowed = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly busy = signal(false);
  readonly error = signal('');
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
  save() {
    if (!this.allowed() || this.busy()) return;
    const errors = this.errorsText
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);
    if (
      !this.confirmed ||
      !/^[A-Za-z0-9_-]{1,64}$/.test(this.studentId.trim()) ||
      !this.topic.trim() ||
      this.topic.trim().length > 160 ||
      this.performance === null ||
      !Number.isFinite(this.performance) ||
      this.performance < 0 ||
      this.performance > 100 ||
      this.attempts === null ||
      !Number.isInteger(this.attempts) ||
      this.attempts < 1 ||
      this.attempts > 10000 ||
      errors.length > 10 ||
      new Set(errors).size !== errors.length ||
      errors.some((value) => value.length > 100) ||
      (this.resolutionTime !== null &&
        (!Number.isFinite(this.resolutionTime) ||
          this.resolutionTime < 0 ||
          this.resolutionTime > 86400))
    ) {
      this.error.set('Revisa los campos y confirma que utilizas datos ficticios.');
      return;
    }
    const request: ProfileRequest = {
      student_id: this.studentId.trim(),
      topic: this.topic.trim(),
      performance: this.performance,
      attempts: this.attempts,
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
