import { navigationItems } from './links';
// Presenta destinos por rol y restaura el foco al cerrar el menú modal.
import { Component, computed, ElementRef, inject, signal, viewChild } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../nucleo/servicios/auth.service';

@Component({
  selector: 'app-workspace-navigation',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav.html',
  styleUrl: './nav.scss',
})
export class NavigationComponent {
  private readonly auth = inject(AuthService);
  readonly panel = viewChild<ElementRef<HTMLDialogElement>>('panel');
  private readonly trigger = viewChild<ElementRef<HTMLButtonElement>>('trigger');
  readonly open = signal(false);
  readonly items = computed(() => {
    const user = this.auth.user();
    if (!user) return [];
    return navigationItems(user.rol);
  });

  constructor() {
    inject(Router)
      .events.pipe(takeUntilDestroyed())
      .subscribe((event) => {
        if (event instanceof NavigationEnd) this.close();
      });
  }
  toggle() {
    if (this.open()) return this.close();
    this.panel()?.nativeElement.showModal();
    this.open.set(true);
  }
  close() {
    if (!this.open()) return;
    this.panel()?.nativeElement.close();
    this.open.set(false);
    this.trigger()?.nativeElement.focus();
  }
  cancel(event: Event) {
    event.preventDefault();
    this.close();
  }
  backdrop(event: MouseEvent) {
    if (event.target === this.panel()?.nativeElement) this.close();
  }
}
