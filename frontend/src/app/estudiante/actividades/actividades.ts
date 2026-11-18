import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AssignmentListState } from '../../compartido/actividades/lista-actividades.state';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  Assignment,
  ASSIGNMENT_STATUS_LABELS,
} from '../../compartido/actividades/actividades.model';
@Component({
  selector: 'app-student-assignments',
  imports: [RouterLink, DatePipe, FormsModule],
  providers: [AssignmentListState],
  templateUrl: './actividades.html',
  styleUrls: ['./actividades.scss', './listado.scss'],
})
export class StudentAssignmentsComponent implements OnInit {
  private readonly listing = inject(AssignmentListState);
  readonly page = this.listing.page;
  readonly loading = this.listing.loading;
  readonly error = this.listing.error;
  readonly search = signal('');
  readonly status = signal('');
  readonly content = signal('');
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  readonly filtered = computed(() =>
    (this.page()?.items ?? []).filter(
      (item) =>
        item.title.toLocaleLowerCase('es').includes(this.search().trim().toLocaleLowerCase('es')) &&
        (!this.status() || item.status === this.status()) &&
        (!this.content() || (this.content() === 'material') === !!item.resource_id),
    ),
  );
  actionLabel(item: Assignment) {
    return item.resource_type === 'QUIZ' ? 'Responder quiz' : item.resource_id
      ? 'Ver recurso'
      : item.status !== 'open'
        ? 'Ver resultados'
        : item.attempts
          ? 'Volver a practicar'
          : 'Resolver actividad';
  }
  ngOnInit() {
    this.load();
  }
  load(offset = 0) {
    this.listing.load(offset, 5);
  }
}
