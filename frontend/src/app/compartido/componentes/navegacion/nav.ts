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
    if (!user)
      return [
        {
          path: '/login',
          label: 'Entrar',
          description: 'Entra a tu espacio de aprendizaje',
        },
      ];
    const links = [{ path: '/inicio', label: 'Inicio', description: 'Tu espacio de trabajo' }];
    if (user.rol === 'student') {
      links.push(
        {
          path: '/actividades',
          label: 'Actividades asignadas',
          description: 'Ejercicios y materiales de tu profesor',
        },
        {
          path: '/practica',
          label: 'Práctica libre',
          description: 'Repaso voluntario con historial personal',
        },
      );
    }
    if (user.rol === 'teacher' || user.rol === 'admin') {
      links.push(
        {
          path: '/documentos',
          label: 'Mis documentos',
          description: 'Sube y prepara tus materiales de clase',
        },
        {
          path: '/recursos',
          label: 'Recursos',
          description: 'Crea recursos o retoma los que guardaste',
        },
        {
          path: '/actividades',
          label: 'Actividades asignadas',
          description: 'Asigna contenido y consulta resultados',
        },
        {
          path: '/busqueda',
          label: 'Buscar fuentes',
          description: 'Consulta tus documentos preparados',
        },
        {
          path: '/perfiles',
          label: 'Perfiles de aprendizaje',
          description: 'Apoyo opcional para adaptar un recurso',
        },
        {
          path: '/metricas',
          label: 'Uso de generación',
          description: 'Consulta solicitudes, tokens y tiempos de generación',
        },
      );
    }
    return links;
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
