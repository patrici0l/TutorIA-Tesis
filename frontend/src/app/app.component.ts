import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { NavigationComponent } from './compartido/componentes/navegacion/navigation.component';
import { AuthService } from './nucleo/servicios/auth.service';

@Component({
  imports: [RouterOutlet, RouterLink, NavigationComponent],
  selector: 'app-root',
  styleUrl: './app.component.scss',
  templateUrl: './app.component.html',
})
export class App {
  readonly auth = inject(AuthService);
  readonly router = inject(Router);
  readonly signingOut = signal(false);
  readonly logoutError = signal('');
  logout() {
    if (this.signingOut()) return;
    this.signingOut.set(true);
    this.logoutError.set('');
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
