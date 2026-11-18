// Abre la actividad autorizada y presenta el banco o material según su contrato.
import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, of, switchMap, tap } from 'rxjs';
import { AssignmentService } from '../../compartido/actividades/actividades.service';
import {
  Assignment,
  ASSIGNMENT_STATUS_LABELS,
} from '../../compartido/actividades/actividades.model';
import { PracticeComponent } from '../practica/practica';
import { ResourceViewComponent } from '../../compartido/recursos/recurso';
import { PRACTICE_BANKS } from '../../compartido/practica/bancos';
import { AuthService } from '../../inicio/sesion.service';

@Component({
  selector: 'app-assignment-practice',
  imports: [RouterLink, PracticeComponent, ResourceViewComponent],
  templateUrl: './resolver.html',
  styleUrl: './resolver.scss',
})
export class AssignmentPracticeComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly service = inject(AssignmentService);
  private readonly destroy = inject(DestroyRef);
  readonly auth = inject(AuthService);
  readonly assignment = signal<Assignment | null>(null);
  readonly sourceOffset = signal(0);
  readonly loading = signal(true);
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  ngOnInit() {
    this.route.paramMap
      .pipe(
        tap(() => {
          this.sourceOffset.set(0);
          this.assignment.set(null);
          this.loading.set(true);
        }),
        switchMap((params) =>
          this.service.detail(params.get('id') ?? '').pipe(catchError(() => of(null))),
        ),
        takeUntilDestroyed(this.destroy),
      )
      .subscribe((item) => {
        this.assignment.set(
          item &&
            (PRACTICE_BANKS.some((b) => b.version === item.version) ||
              (item.version === 'resource-v1' && item.resource))
            ? item
            : null,
        );
        this.loading.set(false);
      });
  }
}
