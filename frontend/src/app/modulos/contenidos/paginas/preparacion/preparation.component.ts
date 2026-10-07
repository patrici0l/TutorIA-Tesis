import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import {
  Difficulty,
  PreparationRequest,
  PreparationResponse,
  ResourceType,
} from '../../modelos/preparation.model';
import { PreparationService } from '../../servicios/preparation.service';

@Component({
  selector: 'app-resource-preparation',
  imports: [FormsModule, RouterLink],
  templateUrl: './preparation.component.html',
  styleUrl: './preparation.component.scss',
})
export class PreparationComponent {
  private readonly service = inject(PreparationService);
  private readonly auth = inject(AuthService);
  private readonly destroy = inject(DestroyRef);
  readonly canPrepare = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly loading = signal(false);
  readonly error = signal('');
  readonly result = signal<PreparationResponse | null>(null);
  readonly resources: { value: ResourceType; label: string; description: string }[] = [
    {
      value: 'EXPLANATION',
      label: 'Explicación',
      description: 'Un concepto paso a paso, con un ejemplo resuelto.',
    },
    {
      value: 'EXERCISE',
      label: 'Ejercicio',
      description: 'Una práctica con pistas y una solución guiada.',
    },
    {
      value: 'QUIZ',
      label: 'Quiz',
      description: 'Preguntas de cuatro opciones con su explicación.',
    },
    {
      value: 'FEEDBACK',
      label: 'Retroalimentación',
      description: 'Una revisión de la respuesta y un siguiente paso.',
    },
  ];
  topic = '';
  objective = '';
  resourceType: ResourceType = 'EXPLANATION';
  difficulty: Difficulty = 'basic';
  questionCount = 3;
  studentAnswer = '';

  clearResult() {
    this.result.set(null);
    this.error.set('');
  }
  changeResource() {
    this.clearResult();
    if (this.resourceType !== 'FEEDBACK') this.studentAnswer = '';
  }
  label(value: ResourceType) {
    return this.resources.find((item) => item.value === value)?.label ?? value;
  }
  description() {
    return this.resources.find((item) => item.value === this.resourceType)?.description;
  }
  prepare() {
    if (!this.canPrepare() || this.loading()) return;
    this.result.set(null);
    const topic = this.topic.trim(),
      objective = this.objective.trim();
    if (
      !topic ||
      topic.length > 160 ||
      !objective ||
      objective.length > 400 ||
      (this.resourceType === 'QUIZ' &&
        (!Number.isInteger(this.questionCount) ||
          this.questionCount < 1 ||
          this.questionCount > 5)) ||
      (this.resourceType === 'FEEDBACK' &&
        (!this.studentAnswer.trim() || this.studentAnswer.length > 2000))
    ) {
      this.error.set('Completa el tema, el objetivo y los campos del recurso.');
      return;
    }
    const request: PreparationRequest = {
      topic,
      learning_objective: objective,
      resource_type: this.resourceType,
      difficulty: this.difficulty,
    };
    if (this.resourceType === 'QUIZ') request.question_count = this.questionCount;
    if (this.resourceType === 'FEEDBACK') request.student_answer = this.studentAnswer.trim();
    this.error.set('');
    this.loading.set(true);
    this.service
      .prepare(request)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.result.set(response);
          this.loading.set(false);
        },
        error: (error: HttpErrorResponse) => {
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo confirmar la preparación. Revisa la conexión antes de volver a enviarla.',
          );
          this.loading.set(false);
        },
      });
  }
}
