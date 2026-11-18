import { NgSelectComponent, NgOptionTemplateDirective } from '@ng-select/ng-select';
import { CourseCatalogService, CourseOption } from '../documentos/asignaturas.service';
// Separa preparación revisable, envío único e historial para evitar generaciones duplicadas.
import {
  Component,
  computed,
  DestroyRef,
  inject,
  signal,
  ViewChild,
  OnInit,
  afterNextRender,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { ResourceViewComponent } from '../../compartido/recursos/recurso';
import { ResourceHistoryComponent } from './historial';
import { ResourceAuditComponent } from './auditoria';
import { ResourceExportComponent } from './exportar';
import { GenerationQuotaComponent } from './cuota';
import { HistoryDetail } from './historial.model';
import { AuthService } from '../../inicio/sesion.service';
import {
  Difficulty,
  GenerationResponse,
  PreparationRequest,
  PreparationResponse,
  ResourceType,
} from '../../compartido/recursos/recursos.model';
import { PreparationService } from './recursos.service';
import { ProfileService } from '../perfiles/perfiles.service';
import { ProfilePage, ProfileSummary } from '../perfiles/perfiles.model';

@Component({
  selector: 'app-resource-preparation',
  imports: [
    FormsModule,
    NgSelectComponent,
    NgOptionTemplateDirective,
    RouterLink,
    ResourceViewComponent,
    ResourceHistoryComponent,
    ResourceAuditComponent,
    ResourceExportComponent,
    GenerationQuotaComponent,
  ],
  templateUrl: './preparar.html',
  styleUrls: ['./preparar.scss', './compacto.scss'],
})
export class PreparationComponent implements OnInit {
  readonly sourceOffset = signal(0);

  private readonly catalog = inject(CourseCatalogService);
  readonly courses = signal<CourseOption[]>([]);
  readonly coursesLoading = signal(false);
  readonly coursesError = signal('');
  readonly inputStep = signal<'course' | 'details'>('course');
  ngOnInit() {
    if (this.canPrepare()) this.loadCourses();
  }
  loadCourses() {
    if (this.coursesLoading()) return;
    this.coursesLoading.set(true);
    this.coursesError.set('');
    this.catalog
      .load()
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (courses) => {
          this.courses.set(courses);
          const chosen = courses.find(
            (item) =>
              item.value.toLocaleLowerCase('es') === this.course.trim().toLocaleLowerCase('es'),
          );
          this.course = chosen?.value ?? '';
          this.coursesLoading.set(false);
        },
        error: () => {
          this.coursesLoading.set(false);
          this.coursesError.set('No se pudieron consultar tus asignaturas. Vuelve a intentarlo.');
        },
      });
  }
  selectedCourse() {
    return this.courses().find(
      (item) => item.value.toLocaleLowerCase('es') === this.course.trim().toLocaleLowerCase('es'),
    );
  }
  chooseCourse() {
    this.clearResult();
    this.inputStep.set('course');
    this.selectedProfile.set(null);
    this.profileMessage.set('');
  }
  showCourse() {
    this.workspaceMode.set('create');
    this.editing.set(true);
    this.inputStep.set('course');
    this.attention.reveal('course-title');
  }
  continueWithCourse() {
    if (!this.selectedCourse()?.enabled || this.coursesLoading()) return;
    this.showEditor();
  }

  private readonly attention = inject(ViewAttention);
  private readonly route = inject(ActivatedRoute);
  readonly choosingAssignment = this.route.snapshot.queryParamMap.get('action') === 'assign';
  constructor() {
    afterNextRender(() => {
      if (this.canPrepare() && this.route.snapshot.queryParamMap.get('view') === 'saved')
        this.showSaved();
    });
  }
  @ViewChild(ResourceHistoryComponent) private history!: ResourceHistoryComponent;
  readonly workspaceMode = signal<'create' | 'saved'>('create');
  readonly editing = signal(true);
  readonly profileMessage = signal('');
  readonly currentStep = computed(() =>
    this.generation()?.resource ? 4 : this.result() ? 3 : this.inputStep() === 'details' ? 2 : 1,
  );

  showEditor() {
    this.workspaceMode.set('create');
    this.editing.set(true);
    this.inputStep.set(this.selectedCourse()?.enabled ? 'details' : 'course');
    this.attention.reveal(this.inputStep() === 'details' ? 'prepare-title' : 'course-title');
  }
  showSaved() {
    this.workspaceMode.set('saved');
    if (!this.history.page()) this.history.load();
    this.attention.reveal('history-title');
  }
  showResult() {
    this.workspaceMode.set('create');
    this.editing.set(false);
    this.attention.reveal('sources-title');
  }
  revealGenerated() {
    this.attention.reveal('generated-title');
  }
  selectProfile(id: string) {
    this.chooseProfile(this.profilePage()?.items.find((profile) => profile.id === id) ?? null);
  }
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
  readonly quotaRefresh = signal(0);
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
  course = this.route.snapshot.queryParamMap.get('course') ?? '';
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
          this.attention.reveal('profile-picker');
        },
        error: () => {
          this.error.set('No se pudieron consultar los perfiles.');
          this.loadingProfiles.set(false);
          this.attention.reveal('resource-error');
        },
      });
  }
  chooseProfile(profile: ProfileSummary | null) {
    if (this.loading() || this.generating() || this.loadingProfiles()) return;
    this.selectedProfile.set(profile);
    if (profile) this.topic = profile.topic;
    this.clearResult();
    this.profileMessage.set(
      profile
        ? `Perfil seleccionado: ${profile.student_id}. Tema: ${profile.topic}. La dificultad se ajustará a su dominio.`
        : 'Personalización desactivada. Puedes elegir la dificultad.',
    );
    this.attention.reveal('profile-feedback');
  }
  difficultyLabel(value: Difficulty) {
    return { basic: 'Básica', intermediate: 'Intermedia', advanced: 'Avanzada' }[value];
  }
  masteryLabel(value: 'low' | 'medium' | 'high') {
    return { low: 'Bajo', medium: 'Medio', high: 'Alto' }[value];
  }

  clearResult() {
    this.editing.set(true);
    this.historyDetail.set(null);
    this.restoredPending.set(false);
    this.sourceOffset.set(0);
    this.result.set(null);
    this.generation.set(null);
    this.sent.set(false);
    this.error.set('');
  }
  restore(detail: HistoryDetail) {
    if (this.loading() || this.generating()) return;
    this.clearResult();
    this.sourceOffset.set(0);
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
    this.showResult();
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
    this.attention.reveal('generation-feedback');
    this.error.set('');
    this.service
      .generate(prepared.id)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.generation.set(response);
          this.generating.set(false);
          this.quotaRefresh.update((value) => value + 1);
          this.attention.reveal(response.resource ? 'generated-title' : 'generation-feedback');
        },
        error: (error: HttpErrorResponse) => {
          this.generating.set(false);
          this.quotaRefresh.update((value) => value + 1);
          // Estos rechazos ocurren antes de reservar; permiten otro envío de la preparación.
          if ([401, 403, 429, 503].includes(error.status)) this.sent.set(false);
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo confirmar el resultado. Evita repetir el envío; podría haberse procesado.',
          );
          this.attention.reveal('resource-error');
        },
      });
  }
  prepare() {
    if (!this.canPrepare() || this.loading() || this.generating()) return;
    this.sourceOffset.set(0);
    this.result.set(null);
    this.historyDetail.set(null);
    const topic = this.topic.trim(),
      objective = this.objective.trim();
    if (
      !this.course.trim() ||
      this.course.trim().length > 160 ||
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
      this.attention.reveal('resource-error');
      return;
    }
    const request: PreparationRequest = {
      course: this.course.trim(),
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
          this.sourceOffset.set(0);
          this.result.set(response);
          this.loading.set(false);
          this.showResult();
        },
        error: (error: HttpErrorResponse) => {
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo confirmar la preparación. Revisa la conexión antes de volver a enviarla.',
          );
          this.loading.set(false);
          this.attention.reveal('resource-error');
        },
      });
  }
}
