// Carga pantallas bajo demanda y aplica el acceso por sesión y rol.
import { Routes } from '@angular/router';
import { authGuard } from './inicio/sesion.guard';
import { practiceExitGuard } from './compartido/practica/salida-practica.service';

export const routes: Routes = [
  { path: 'solicitar', title: 'Solicitar contenido', canActivate: [authGuard],
    loadComponent: () => import('./estudiante/solicitar').then(m => m.StudentContentComponent) },
  { path: 'accesos', title: 'Acceso de estudiantes', canActivate: [authGuard],
    loadComponent: () => import('./profesor/accesos').then(m => m.LearningAccessComponent) },
  { path: 'fuentes-externas', title: 'Fuentes externas', canActivate: [authGuard],
    loadComponent: () => import('./profesor/documentos/fuentes-externas').then(m => m.ExternalSourcesComponent) },
  {
    path: 'actividades',
    title: 'Actividades asignadas',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./compartido/actividades/actividades').then((m) => m.AssignmentsComponent),
  },
  {
    path: 'actividades/:id',
    title: 'Resolver actividad',
    canActivate: [authGuard],
    canDeactivate: [practiceExitGuard],
    loadComponent: () =>
      import('./estudiante/actividades/resolver').then((m) => m.AssignmentPracticeComponent),
  },
  {
    path: 'practica',
    title: 'Práctica libre',
    canActivate: [authGuard],
    canDeactivate: [practiceExitGuard],
    loadComponent: () => import('./estudiante/practica/practica').then((m) => m.PracticeComponent),
  },
  {
    path: 'metricas',
    title: 'Uso de generación',
    canActivate: [authGuard],
    loadComponent: () => import('./profesor/metricas/metricas').then((m) => m.MetricsComponent),
  },
  {
    path: 'perfiles',
    title: 'Perfiles de aprendizaje',
    canActivate: [authGuard],
    loadComponent: () => import('./profesor/perfiles/perfiles').then((m) => m.ProfilesComponent),
  },
  {
    path: 'recursos',
    title: 'Recursos',
    canActivate: [authGuard],
    loadComponent: () => import('./profesor/recursos/preparar').then((m) => m.PreparationComponent),
  },
  {
    path: 'busqueda',
    title: 'Búsqueda de fuentes',
    canActivate: [authGuard],
    loadComponent: () => import('./profesor/busqueda/busqueda').then((m) => m.SearchComponent),
  },
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  {
    path: 'login',
    title: 'Entrar',
    loadComponent: () => import('./inicio/login').then((m) => m.LoginComponent),
  },
  {
    path: 'documentos',
    title: 'Documentos del curso',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./profesor/documentos/documentos').then((m) => m.DocumentsComponent),
  },
  {
    path: 'inicio',
    title: 'Inicio',
    canActivate: [authGuard],
    loadComponent: () => import('./inicio/inicio').then((m) => m.InicioComponent),
  },
  { path: '**', redirectTo: 'inicio' },
];
