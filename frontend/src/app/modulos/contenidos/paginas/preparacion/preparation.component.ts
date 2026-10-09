import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ResourceViewComponent } from '../../componentes/resource-view/resource-view.component';
import { ResourceHistoryComponent } from '../../componentes/resource-history/resource-history.component';
import { ResourceAuditComponent } from '../../componentes/resource-audit/resource-audit.component';
import { HistoryDetail } from '../../modelos/history.model';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import {
  Difficulty,
  GenerationResponse,
  PreparationRequest,
  PreparationResponse,
  ResourceType,
} from '../../modelos/preparation.model';
import { PreparationService } from '../../servicios/preparation.service';
import { ProfileService } from '../../../perfiles/servicios/profile.service';
import { ProfilePage, ProfileSummary } from '../../../perfiles/modelos/profile.model';

@Component({
  selector: 'app-resource-preparation',
  imports: [
    FormsModule,
    RouterLink,
    ResourceViewComponent,
    ResourceHistoryComponent,
    ResourceAuditComponent,
  ],
  templateUrl: './preparation.component.html',
  styleUrl: './preparation.component.scss',
})
export class PreparationComponent {
  private readonly service = inject(PreparationService);
  private readonly auth = inject(AuthService);
  private readonly destroy = inject(DestroyRef);
  private readonly profiles = inject(ProfileService);
  readonly profilePage = signal<ProfilePage | null>(null);
  readonly selectedProfile = signal<ProfileSummary | null>(null);
  readonly loadingProfiles = signal(false);
  readonly canPrepare = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly loading = signal(false);
  readonly generating = signal(false);
  readonly generation = signal<GenerationResponse | null>(null);
  readonly sent = signal(false);
  readonly error = signal('');
  readonly result = signal<PreparationResponse | null>(null);
  readonly restoredPending = signal(false);
  readonly historyDetail = signal<HistoryDetail | null>(null);
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

  loadProfiles(offset = 0) {
    if (!this.canPrepare() || this.loadingProfiles() || this.loading() || this.generating()) return;
    this.loadingProfiles.set(true);
    this.error.set('');
    this.profiles
      .page(offset)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (page) => {
          this.profilePage.set(page);
          this.loadingProfiles.set(false);
        },
        error: () => {
          this.error.set('No se pudieron consultar los perfiles.');
          this.loadingProfiles.set(false);
        },
      });
  }
  chooseProfile(profile: ProfileSummary | null) {
    if (this.loading() || this.generating() || this.loadingProfiles()) return;
    this.selectedProfile.set(profile);
    if (profile) this.topic = profile.topic;
    this.clearResult();
  }
  difficultyLabel(value: Difficulty) {
    return { basic: 'Básica', intermediate: 'Intermedia', advanced: 'Avanzada' }[value];
  }
  masteryLabel(value: 'low' | 'medium' | 'high') {
    return { low: 'Bajo', medium: 'Medio', high: 'Alto' }[value];
  }

  clearResult() {
    this.historyDetail.set(null);
    this.restoredPending.set(false);
    this.result.set(null);
    this.generation.set(null);
    this.sent.set(false);
    this.error.set('');
  }
  restore(detail: HistoryDetail) {
    if (this.loading() || this.generating()) return;
    this.clearResult();
    this.result.set(detail.preparation);
    this.historyDetail.set(detail);
    this.sent.set(detail.status !== 'prepared');
    this.restoredPending.set(detail.status === 'generating');
    if (detail.status === 'succeeded' || detail.status === 'failed') {
      this.generation.set({
        id: detail.preparation.id,
        status: detail.status,
        resource: detail.resource,
        message: detail.message,
      });
    }
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
  generate() {
    const prepared = this.result();
    if (!prepared || this.generating() || this.sent() || !this.canPrepare()) return;
    this.sent.set(true);
    this.historyDetail.set(null);
    this.generating.set(true);
    this.error.set('');
    this.service
      .generate(prepared.id)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.generation.set(response);
          this.generating.set(false);
        },
        error: (error: HttpErrorResponse) => {
          this.generating.set(false);
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo confirmar el resultado. Evita repetir el envío; podría haberse procesado.',
          );
        },
      });
  }
  prepare() {
    if (!this.canPrepare() || this.loading() || this.generating()) return;
    this.result.set(null);
    this.historyDetail.set(null);
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
    if (this.selectedProfile()) request.profile_id = this.selectedProfile()!.id;
    this.error.set('');
    this.loading.set(true);
    this.service
      .prepare(request)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.generation.set(null);
          this.sent.set(false);
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
