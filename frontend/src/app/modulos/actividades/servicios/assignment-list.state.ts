import { Injectable, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AssignmentPage } from '../modelos/assignment.model';
import { AssignmentService } from './assignment.service';

// Estado por pantalla; el servicio HTTP sigue siendo compartido y sin estado de vista.
@Injectable()
export class AssignmentListState {
  private readonly service = inject(AssignmentService);
  private readonly destroy = inject(DestroyRef);
  readonly page = signal<AssignmentPage | null>(null);
  readonly loading = signal(false);
  readonly error = signal('');
  load(offset = 0) {
    if (this.loading()) return;
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
}
