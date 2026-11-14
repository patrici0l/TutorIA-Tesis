import { Component, input } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Assignment, ASSIGNMENT_STATUS_LABELS } from './actividades.model';
import { PRACTICE_BANKS } from '../practica/bancos';
@Component({
  selector: 'app-assignment-card',
  imports: [DatePipe],
  templateUrl: './tarjeta.html',
  styleUrl: './tarjeta.scss',
})
export class AssignmentCardComponent {
  readonly item = input.required<Assignment>();
  readonly showRecipient = input(false);
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  bankTitle(version: string) {
    if (version === 'resource-v1') return 'Material de estudio';
    return PRACTICE_BANKS.find((b) => b.version === version)?.title ?? 'Práctica anterior';
  }
}
