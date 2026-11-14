import { DOCUMENT } from '@angular/common';
import { afterNextRender, inject, Injectable, Injector } from '@angular/core';

// Lleva al resultado solicitado después de renderizarlo, también dentro de un diálogo.
@Injectable({ providedIn: 'root' })
export class ViewAttention {
  private readonly document = inject(DOCUMENT);
  private readonly injector = inject(Injector);
  private pending = 0;

  reveal(target: string | HTMLElement) {
    const request = ++this.pending;
    afterNextRender(
      () => {
        if (request !== this.pending) return;
        const element = typeof target === 'string' ? this.document.getElementById(target) : target;
        if (!element?.isConnected || element.closest('[hidden], details:not([open])')) return;
        const dialog = element.closest('dialog');
        if (dialog && !dialog.open) return;
        const reduced = this.document.defaultView?.matchMedia?.(
          '(prefers-reduced-motion: reduce)',
        ).matches;
        element.focus({ preventScroll: true });
        element.scrollIntoView?.({ behavior: reduced ? 'instant' : 'smooth', block: 'start' });
        if (!reduced) {
          element.animate?.(
            [
              { outline: '3px solid transparent' },
              { outline: '3px solid var(--gold)' },
              { outline: '3px solid transparent' },
            ],
            { duration: 900, easing: 'ease-out' },
          );
        }
      },
      { injector: this.injector },
    );
  }
}
