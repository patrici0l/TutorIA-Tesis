import { inject, Injectable } from '@angular/core';
import { CanDeactivateFn } from '@angular/router';

// Una práctica puede estar directamente en la ruta o dentro de una actividad.
@Injectable({ providedIn: 'root' })
export class PracticeExitService {
  private active: { confirm: () => boolean | Promise<boolean> } | null = null;

  register(confirm: () => boolean | Promise<boolean>): () => void {
    const current = { confirm };
    this.active = current;
    return () => {
      if (this.active === current) this.active = null;
    };
  }

  canLeave(): boolean | Promise<boolean> {
    return this.active?.confirm() ?? true;
  }
}

export const practiceExitGuard: CanDeactivateFn<unknown> = () =>
  inject(PracticeExitService).canLeave();
