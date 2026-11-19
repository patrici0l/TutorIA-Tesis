// Compone la sesión visible y el cierre de acceso en el shell de la aplicación.
import { afterNextRender, Component, DestroyRef, ElementRef, inject, signal, viewChild } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { NavigationComponent } from './compartido/navegacion/navegacion';
import { PracticeExitService } from './compartido/practica/salida-practica.service';
import { AuthService } from './inicio/sesion.service';

@Component({
  imports: [RouterOutlet, RouterLink, NavigationComponent],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html',
  host: { '[style.--site-header-height]': "headerHeight() + 'px'" },
})
export class App {
  readonly auth = inject(AuthService);
  readonly router = inject(Router);
  readonly signingOut = signal(false);
  readonly checkingExit = signal(false);
  readonly logoutError = signal('');
  readonly headerHeight = signal(0);
  private readonly header = viewChild<ElementRef<HTMLElement>>('siteHeader');
  private readonly destroyRef = inject(DestroyRef);
  private readonly practiceExit = inject(PracticeExitService);

  constructor() {
    afterNextRender(() => {
      const header = this.header()?.nativeElement;
      if (!header) return;
      const measureHeader = () => this.headerHeight.set(Math.ceil(header.getBoundingClientRect().height));
      measureHeader();
      if (typeof ResizeObserver !== 'undefined') {
        const observer = new ResizeObserver(measureHeader);
        observer.observe(header);
        this.destroyRef.onDestroy(() => observer.disconnect());
      }
    });
  }

  async logout() {
    if (this.signingOut() || this.checkingExit()) return;
    this.checkingExit.set(true);
    this.logoutError.set('');
    try {
      if (!(await this.practiceExit.canLeave())) return;
    } catch {
      this.logoutError.set('No se pudo comprobar la práctica pendiente. Inténtalo nuevamente.');
      return;
    } finally {
      this.checkingExit.set(false);
    }
    this.signingOut.set(true);
    this.auth.logout().subscribe({
      next: () => {
        this.signingOut.set(false);
        void this.router.navigateByUrl('/login');
      },
      error: () => {
        this.signingOut.set(false);
        this.logoutError.set('No se pudo cerrar la sesión. Inténtalo nuevamente.');
      },
    });
  }
}
