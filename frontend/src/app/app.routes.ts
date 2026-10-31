// Carga pantallas bajo demanda y aplica el acceso por sesión y rol.
import { Routes } from '@angular/router';
import { authGuard } from './nucleo/guardias/auth.guard';

export const routes: Routes = [
  {
    path: 'actividades',
    title: 'Actividades asignadas',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/estudiantes/paginas/actividades/assignments').then(
        (m) => m.AssignmentsComponent,
      ),
  },
  {
    path: 'actividades/:id',
    title: 'Resolver actividad',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/estudiantes/paginas/actividades/resolve').then(
        (m) => m.AssignmentPracticeComponent,
      ),
  },
  {
    path: 'practica',
    title: 'Práctica libre',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/estudiantes/paginas/practica/practice').then((m) => m.PracticeComponent),
  },
  {
    path: 'metricas',
    title: 'Uso de generación',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/metricas/paginas/metricas/metrics').then((m) => m.MetricsComponent),
  },
  {
    path: 'perfiles',
    title: 'Perfiles de aprendizaje',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/perfiles/paginas/perfiles/profiles').then((m) => m.ProfilesComponent),
  },
  {
    path: 'recursos',
    title: 'Recursos',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/contenidos/paginas/preparacion/prepare').then(
        (m) => m.PreparationComponent,
      ),
  },
  {
    path: 'busqueda',
    title: 'Búsqueda de fuentes',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/rag/paginas/busqueda/search').then((m) => m.SearchComponent),
  },
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  {
    path: 'login',
    title: 'Entrar',
    loadComponent: () =>
      import('./modulos/autenticacion/paginas/login/login').then((m) => m.LoginComponent),
  },
  {
    path: 'documentos',
    title: 'Documentos del curso',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/documentos/paginas/documentos/documentos').then(
        (m) => m.DocumentsComponent,
      ),
  },
  {
    path: 'inicio',
    title: 'Inicio',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/inicio/paginas/inicio/inicio').then((m) => m.InicioComponent),
  },
  { path: '**', redirectTo: 'inicio' },
];
