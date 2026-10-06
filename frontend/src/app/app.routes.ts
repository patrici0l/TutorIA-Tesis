import { Routes } from '@angular/router';
import { authGuard } from './nucleo/guardias/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  {
    path: 'login',
    title: 'Acceso UPS | TutorIA',
    loadComponent: () =>
      import('./modulos/autenticacion/paginas/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'inicio',
    title: 'Inicio | TutorIA-Lucero',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/inicio/paginas/inicio/inicio.component').then((m) => m.InicioComponent),
  },
  { path: '**', redirectTo: 'inicio' },
];
