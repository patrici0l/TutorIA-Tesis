import { Component, inject } from '@angular/core';
import { AuthService } from '../../inicio/sesion.service';
import { TeacherAssignmentsComponent } from '../../profesor/actividades/actividades';
import { StudentAssignmentsComponent } from '../../estudiante/actividades/actividades';
@Component({
  selector: 'app-assignments',
  imports: [TeacherAssignmentsComponent, StudentAssignmentsComponent],
  templateUrl: './actividades.html',
  styleUrl: './actividades.scss',
})
export class AssignmentsComponent {
  readonly auth = inject(AuthService);
}
