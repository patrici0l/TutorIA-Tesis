import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, of, switchMap, tap } from 'rxjs';
import {
  Assignment,
  AssignmentService,
  ASSIGNMENT_STATUS_LABELS,
} from '../../servicios/assignment.service';
import { PracticeComponent } from '../practica/practice.component';
import { PRACTICE_BANKS } from '../../modelos/practice-bank';
import { AuthService } from '../../../../nucleo/servicios/auth.service';

@Component({
  selector: 'app-assignment-practice',
  imports: [RouterLink, PracticeComponent],
  templateUrl: './assignment-practice.component.html',
  styleUrl: './assignment-practice.component.scss',
})
export class AssignmentPracticeComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly service = inject(AssignmentService);
  private readonly destroy = inject(DestroyRef);
  readonly auth = inject(AuthService);
  readonly assignment = signal<Assignment | null>(null);
  readonly loading = signal(true);
  readonly statusLabels = ASSIGNMENT_STATUS_LABELS;
  ngOnInit() {
    this.route.paramMap
      .pipe(
        tap(() => {
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
          item && PRACTICE_BANKS.some((b) => b.version === item.version) ? item : null,
        );
        this.loading.set(false);
      });
  }
}
