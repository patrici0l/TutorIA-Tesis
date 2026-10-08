import { Routes } from '@angular/router';
import { authGuard } from './nucleo/guardias/auth.guard';

export const routes: Routes = [
  {
    path: 'perfiles',
    title: 'Perfiles de aprendizaje | TutorIA',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/perfiles/paginas/perfiles/profiles.component').then(
        (m) => m.ProfilesComponent,
      ),
  },
  {
    path: 'recursos',
    title: 'Preparar recursos | TutorIA',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/contenidos/paginas/preparacion/preparation.component').then(
        (m) => m.PreparationComponent,
      ),
  },
  {
    path: 'busqueda',
    title: 'Búsqueda de fuentes | TutorIA',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/rag/paginas/busqueda/search.component').then((m) => m.SearchComponent),
  },
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  {
    path: 'login',
    title: 'Acceso UPS | TutorIA',
    loadComponent: () =>
      import('./modulos/autenticacion/paginas/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'documentos',
    title: 'Documentos del curso | TutorIA',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modulos/documentos/paginas/documentos/documentos.component').then(
        (m) => m.DocumentsComponent,
      ),
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
