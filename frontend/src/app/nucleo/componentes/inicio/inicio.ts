import { Component, inject } from '@angular/core';
import { AuthService } from '../../servicios/auth.service';
import { TeacherHomeComponent } from '../../../modulos/docente/inicio/inicio';
import { StudentHomeComponent } from '../../../modulos/estudiante/inicio/inicio';
@Component({
  selector: 'app-inicio',
  imports: [TeacherHomeComponent, StudentHomeComponent],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
})
export class InicioComponent {
  readonly auth = inject(AuthService);
}
