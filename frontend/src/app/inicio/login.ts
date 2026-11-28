// Selecciona el acceso disponible según la configuración mock o CAS del servidor.
import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from './sesion.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class LoginComponent implements OnInit {
  readonly auth = inject(AuthService);
  readonly denied = inject(ActivatedRoute).snapshot.queryParamMap.has('error');
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  readonly loginMode = signal<'mock' | 'cas' | null>(null);
  readonly loading = signal(true);
  readonly failed = signal(false);

  readonly visible = signal(false);
  readonly accounts = signal(false);
  readonly message = signal('');
  readonly submitting = signal(false);

  signIn(email: string, password: string) {
    if (this.submitting()) return;
    this.submitting.set(true);
    this.message.set('');
    this.auth.login(email, password).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => window.location.assign('/inicio'),
      error: (error) => {
        this.submitting.set(false);
        this.message.set(error.status === 401 ? 'Correo o contraseña incorrectos.' : 'No se pudo iniciar sesión.');
      },
    });
  }

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.failed.set(false);
    this.loginMode.set(null);
    this.auth
      .ensureSession()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((valid) => {
        if (valid) {
          void this.router.navigateByUrl('/inicio');
        } else if (this.auth.unavailable()) {
          this.failed.set(true);
          this.loading.set(false);
        } else {
          this.auth
            .configuration()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
              next: (configuration) => {
                this.accounts.set(!!configuration.accounts);
                this.loginMode.set(configuration.auth_mode);
                this.loading.set(false);
              },
              error: () => {
                this.failed.set(true);
                this.loading.set(false);
              },
            });
        }
      });
  }
}
