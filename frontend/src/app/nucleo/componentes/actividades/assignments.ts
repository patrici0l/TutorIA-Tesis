import { Component, inject } from '@angular/core';
import { AuthService } from '../../servicios/auth.service';
import { TeacherAssignmentsComponent } from '../../../modulos/docente/actividades/assignments';
import { StudentAssignmentsComponent } from '../../../modulos/estudiante/actividades/assignments';
@Component({
  selector: 'app-assignments',
  imports: [TeacherAssignmentsComponent, StudentAssignmentsComponent],
  templateUrl: './assignments.html',
  styleUrl: './assignments.scss',
})
export class AssignmentsComponent {
  readonly auth = inject(AuthService);
}
