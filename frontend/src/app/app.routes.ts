import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  {
    path: 'inicio',
    title: 'Inicio | TutorIA-Lucero',
    loadComponent: () =>
      import('./modulos/inicio/paginas/inicio/inicio.component').then((m) => m.InicioComponent),
  },
  { path: '**', redirectTo: 'inicio' },
];
