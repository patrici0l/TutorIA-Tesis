import { Component, inject } from '@angular/core';
import { AuthService } from './sesion.service';
import { TeacherHomeComponent } from '../profesor/inicio';
import { StudentHomeComponent } from '../estudiante/inicio';
@Component({
  selector: 'app-inicio',
  imports: [TeacherHomeComponent, StudentHomeComponent],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class InicioComponent {
  readonly auth = inject(AuthService);
}
