import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HealthService } from '../../../../nucleo/servicios/health.service';
import { HealthResponse, isHealthResponse } from '../../../../nucleo/modelos/health.model';

@Component({
  selector: 'app-inicio',
  templateUrl: './inicio.component.html',
  styleUrl: './inicio.component.scss',
})
export class InicioComponent implements OnInit {
  private readonly healthService = inject(HealthService);
  private readonly destroyRef = inject(DestroyRef);
  readonly loading = signal(false);
  readonly health = signal<HealthResponse | null>(null);
  readonly error = signal(false);
  readonly checkedAt = signal('');

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    if (this.loading()) return;
    this.loading.set(true);
    this.error.set(false);
    this.health.set(null);
    this.healthService
      .check()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.health.set(result);
          this.finish();
        },
        error: (error: unknown) => {
          if (
            error instanceof HttpErrorResponse &&
            error.status === 503 &&
            isHealthResponse(error.error)
          ) {
            this.health.set(error.error);
          } else {
            this.error.set(true);
          }
          this.finish();
        },
      });
  }

  private finish() {
    this.loading.set(false);
    this.checkedAt.set(
      new Date().toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' }),
    );
  }
}
