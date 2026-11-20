import { ViewAttention } from '../../compartido/atencion-vista.service';
// Reabre recursos persistidos por identificador sin consumir otra inferencia.
import { Component, DestroyRef, inject, input, output, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { PreparationService } from './recursos.service';
import { GenerationStatus, HistoryDetail, HistoryPage } from './historial.model';

@Component({
  selector: 'app-resource-history',
  imports: [DatePipe, RouterLink],
  templateUrl: './historial.html',
  styleUrl: './historial.scss',
})
export class ResourceHistoryComponent {
  private readonly attention = inject(ViewAttention);
  readonly selectedId = signal<string | null>(null);
  readonly types = {
    EXPLANATION: 'Explicación',
    EXAMPLE: 'Ejemplo resuelto',
    HINT: 'Pista',
    EXERCISE: 'Ejercicio',
    QUIZ: 'Quiz',
    FEEDBACK: 'Retroalimentación',
  };
  readonly difficulties = { basic: 'Básica', intermediate: 'Intermedia', advanced: 'Avanzada' };
  private readonly service = inject(PreparationService);
  private readonly destroy = inject(DestroyRef);
  readonly locked = input(false);
  readonly assignmentMode = input(false);
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
  readonly actionLabels: Record<GenerationStatus, string> = {
    prepared: 'Continuar preparación',
    generating: 'Consultar estado',
    succeeded: 'Abrir recurso',
    failed: 'Ver detalle del fallo',
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
          this.attention.reveal('history-title');
        },
        error: () => {
          this.error.set('No se pudo cargar el historial. Puedes volver a consultarlo.');
          this.attention.reveal('history-error');
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
          this.selectedId.set(id);
          this.selected.emit(detail);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('El recurso no está disponible. Actualiza el historial.');
          this.attention.reveal('history-error');
          this.busy.set(false);
        },
      });
  }
}
