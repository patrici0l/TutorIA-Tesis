import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AssignmentListState } from '../../compartido/actividades/lista-actividades.state';
import { AssignmentCardComponent } from '../../compartido/actividades/tarjeta';
@Component({
  selector: 'app-student-assignments',
  imports: [RouterLink, AssignmentCardComponent],
  providers: [AssignmentListState],
  templateUrl: './actividades.html',
  styleUrl: './actividades.scss',
})
export class StudentAssignmentsComponent implements OnInit {
  private readonly listing = inject(AssignmentListState);
  readonly page = this.listing.page;
  readonly loading = this.listing.loading;
  readonly error = this.listing.error;
  ngOnInit() {
    this.load();
  }
  load(offset = 0) {
    this.listing.load(offset);
  }
}
