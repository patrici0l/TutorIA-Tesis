import { Component, DestroyRef, inject, input, output, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { PreparationService } from '../../servicios/preparation.service';
import { GenerationStatus, HistoryDetail, HistoryPage } from '../../modelos/history.model';

@Component({
  selector: 'app-resource-history',
  imports: [DatePipe],
  templateUrl: './resource-history.component.html',
  styleUrl: './resource-history.component.scss',
})
export class ResourceHistoryComponent {
  readonly types = {
    EXPLANATION: 'Explicación',
    EXERCISE: 'Ejercicio',
    QUIZ: 'Quiz',
    FEEDBACK: 'Retroalimentación',
  };
  readonly difficulties = { basic: 'Básica', intermediate: 'Intermedia', advanced: 'Avanzada' };
  private readonly service = inject(PreparationService);
  private readonly destroy = inject(DestroyRef);
  readonly locked = input(false);
  readonly selected = output<HistoryDetail>();
  readonly page = signal<HistoryPage | null>(null);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly labels: Record<GenerationStatus, string> = {
    prepared: 'Preparado',
    generating: 'En proceso',
    succeeded: 'Generado',
    failed: 'Sin resultado',
  };
  load(offset = 0) {
    if (this.busy() || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.service
      .history(offset)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (page) => {
          this.page.set(page);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('No se pudo cargar el historial. Puedes volver a consultarlo.');
          this.busy.set(false);
        },
      });
  }
  open(id: string) {
    if (this.busy() || this.locked()) return;
    this.busy.set(true);
    this.error.set('');
    this.service
      .detail(id)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (detail) => {
          this.selected.emit(detail);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('El recurso no está disponible. Actualiza el historial.');
          this.busy.set(false);
        },
      });
  }
}
