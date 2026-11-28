import { Component, inject } from '@angular/core';
import { AuthService } from '../../inicio/sesion.service';
import { ClassSimulationComponent } from '../../profesor/perfiles/simulacion';
import { StudentAssignmentsComponent } from '../../estudiante/actividades/actividades';
@Component({
  selector: 'app-assignments',
  imports: [ClassSimulationComponent, StudentAssignmentsComponent],
  templateUrl: './actividades.html',
  styleUrl: './actividades.scss',
})
export class AssignmentsComponent {
  readonly auth = inject(AuthService);
}
