import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { MetricsSummary } from '../../modelos/metrics.model';
import { MetricsService } from '../../servicios/metrics.service';

@Component({
  selector: 'app-generation-metrics',
  imports: [DatePipe, DecimalPipe, RouterLink],
  templateUrl: './metrics.component.html',
  styleUrl: './metrics.component.scss',
})
export class MetricsComponent {
  private readonly auth = inject(AuthService);
  private readonly service = inject(MetricsService);
  private readonly destroy = inject(DestroyRef);
  readonly allowed = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly busy = signal(false);
  readonly error = signal('');
  readonly summary = signal<MetricsSummary | null>(null);
  readonly tokenLabels = [
    { key: 'input_tokens', label: 'Entrada' },
    { key: 'output_tokens', label: 'Salida' },
    { key: 'total_tokens', label: 'Total reportado' },
  ] as const;

  constructor() {
    this.load();
  }
  load() {
    if (!this.allowed() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.summary.set(null);
    this.service
      .summary()
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (summary) => {
          this.summary.set(summary);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('No se pudieron consultar tus métricas. Puedes volver a intentarlo.');
          this.busy.set(false);
        },
      });
  }
}
