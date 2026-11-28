import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from './sesion.service';
import { TeacherHomeComponent } from '../profesor/inicio';
import { StudentHomeComponent } from '../estudiante/inicio';
@Component({
  selector: 'app-inicio',
  imports: [RouterLink, TeacherHomeComponent, StudentHomeComponent],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class InicioComponent {
  readonly auth = inject(AuthService);
}
