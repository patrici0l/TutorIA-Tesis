import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { finalize } from 'rxjs';
import { AuthService } from '../inicio/sesion.service';
import { ViewAttention } from '../compartido/atencion-vista.service';
import { ResourceViewComponent } from '../compartido/recursos/recurso';
import {
  Difficulty,
  EducationalResource,
  GenerationResponse,
  PreparationResponse,
  ResourceType,
} from '../compartido/recursos/recursos.model';
import { HistoryDetail, HistoryPage } from '../profesor/recursos/historial.model';
import { GenerationQuota } from '../profesor/recursos/recursos.service';

interface LearningCourse {
  id: string;
  course: string;
  teacher: string;
}

export interface RequestTypeOption {
  value: ResourceType;
  label: string;
  description: string;
  placeholder: string;
}

type RequestStatus = 'prepared' | 'generating' | 'succeeded' | 'failed';

@Component({
  selector: 'app-student-content',
  imports: [FormsModule, DatePipe, ResourceViewComponent],
  templateUrl: './solicitar.html',
  styleUrls: ['./solicitar.scss', './solicitar-detalle.scss'],
})
export class StudentContentComponent {
  readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly destroy = inject(DestroyRef);
  private readonly attention = inject(ViewAttention);
  private copyTimer: ReturnType<typeof setTimeout> | null = null;

  readonly courses = signal<LearningCourse[]>([]);
  readonly loadingCourses = signal(true);
  readonly coursesError = signal(false);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly message = signal('');
  readonly prepared = signal<PreparationResponse | null>(null);
  readonly resource = signal<EducationalResource | null>(null);
  readonly sent = signal(false);
  readonly quota = signal<GenerationQuota | null>(null);
  readonly history = signal<HistoryPage | null>(null);
  readonly historyError = signal(false);
  readonly historyLoading = signal(false);

  readonly activeView = signal<'form' | 'detail'>('form');
  readonly copiedEmail = signal(false);
  readonly openedStatus = signal<RequestStatus | null>(null);
  readonly currentStep = computed<1 | 2 | 3>(() =>
    this.activeView() === 'form' || !this.prepared() ? 1 : this.resource() ? 3 : 2,
  );

  readonly types: RequestTypeOption[] = [
    {
      value: 'EXPLANATION',
      label: 'Una explicación',
      description: 'Concepto explicado paso a paso con un ejemplo resuelto basado en tus materiales.',
      placeholder:
        'Por ejemplo: comprender qué es un espacio muestral y cómo se relaciona con los eventos.',
    },
    {
      value: 'EXAMPLE',
      label: 'Un ejemplo resuelto',
      description: 'Un problema concreto desarrollado paso a paso hasta llegar al resultado.',
      placeholder: 'Por ejemplo: resolver paso a paso un problema de probabilidad condicional.',
    },
    {
      value: 'EXERCISE',
      label: 'Un ejercicio para practicar',
      description: 'Una práctica con pistas progresivas y solución guiada para entrenar.',
      placeholder: 'Por ejemplo: un ejercicio para aplicar la regla de la cadena en derivadas.',
    },
    {
      value: 'QUIZ',
      label: 'Un cuestionario',
      description: 'Preguntas interactivas de opción múltiple con explicación al terminar.',
      placeholder: 'Por ejemplo: preguntas de repaso sobre reglas básicas de derivación.',
    },
    {
      value: 'HINT',
      label: 'Una pista',
      description: 'Orientación para avanzar sin revelar la respuesta final.',
      placeholder: 'Incluye el enunciado del ejercicio y el paso donde tienes dudas.',
    },
    {
      value: 'FEEDBACK',
      label: 'Revisar mi respuesta',
      description: 'Diagnóstico, corrección y siguiente paso a partir de tu procedimiento.',
      placeholder: 'Incluye el enunciado del ejercicio que intentaste resolver.',
    },
  ];

  accessId = '';
  topic = '';
  objective = '';
  kind: ResourceType = 'EXPLANATION';
  difficulty: Difficulty = 'basic';
  answer = '';
  questionCount = 3;

  readonly statuses: Record<RequestStatus, string> = {
    prepared: 'Listo para generar',
    generating: 'En proceso',
    succeeded: 'Disponible',
    failed: 'No se pudo generar',
  };

  constructor() {
    this.destroy.onDestroy(() => {
      if (this.copyTimer) clearTimeout(this.copyTimer);
    });
    if (this.auth.user()?.rol === 'student') {
      this.loadCourses();
      this.loadQuota();
      this.loadHistory();
    }
  }

  loadCourses() {
    this.loadingCourses.set(true);
    this.coursesError.set(false);
    this.http
      .get<LearningCourse[]>('/api/v1/learning/courses')
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (rows) => {
          this.courses.set(rows);
          if (this.accessId && !rows.some((r) => r.id === this.accessId)) {
            this.accessId = '';
          }
          if (!this.accessId && rows.length === 1) {
            this.accessId = rows[0].id;
          }
          this.loadingCourses.set(false);
        },
        error: () => {
          this.loadingCourses.set(false);
          this.coursesError.set(true);
        },
      });
  }

  loadQuota() {
    this.quota.set(null);
    this.http
      .get<GenerationQuota>('/api/v1/learning/quota')
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (q) => this.quota.set(q),
        error: () => this.quota.set(null),
      });
  }

  loadHistory(offset = 0) {
    if (this.historyLoading()) return;
    this.historyError.set(false);
    this.historyLoading.set(true);
    this.http
      .get<HistoryPage>('/api/v1/learning/history', { params: { offset } })
      .pipe(
        takeUntilDestroyed(this.destroy),
        finalize(() => this.historyLoading.set(false)),
      )
      .subscribe({
        next: (h) => this.history.set(h),
        error: () => this.historyError.set(true),
      });
  }

  reset() {
    this.prepared.set(null);
    this.resource.set(null);
    this.sent.set(false);
    this.openedStatus.set(null);
    this.message.set('');
    this.error.set('');
  }

  clearError() {
    this.error.set('');
  }

  selectedType(): RequestTypeOption {
    return this.types.find((t) => t.value === this.kind) ?? this.types[0];
  }

  difficultyLabel(value?: Difficulty | null): string {
    if (!value) return '';
    return { basic: 'Básico', intermediate: 'Intermedio', advanced: 'Avanzado' }[value] ?? '';
  }

  sourceLocation(source: {
    source_kind?: 'page' | 'paragraph';
    source_index?: number;
    position?: number;
  }): string {
    if (source.source_index != null) {
      return `${source.source_kind === 'page' ? 'Página' : 'Párrafo'} ${source.source_index}`;
    }
    if (source.position != null) {
      return `Fragmento ${source.position + 1}`;
    }
    return '';
  }

  showForm() {
    this.activeView.set('form');
    this.attention.reveal('student-form-title');
  }

  showDetail() {
    if (!this.prepared()) return;
    this.activeView.set('detail');
    this.attention.reveal('student-sources');
  }

  startNewRequest() {
    if (this.busy()) return;
    this.reset();
    this.topic = '';
    this.objective = '';
    this.answer = '';
    this.activeView.set('form');
    this.attention.reveal('student-form-title');
  }

  editCurrentRequest() {
    if (this.busy()) return;
    const p = this.prepared();
    if (p) {
      if (p.topic) this.topic = p.topic;
      if (p.learning_objective) this.objective = p.learning_objective;
      if (p.resource_type) this.kind = p.resource_type;
      if (p.difficulty) this.difficulty = p.difficulty;
      if (typeof p.question_count === 'number') this.questionCount = p.question_count;
    }
    this.error.set('');
    this.activeView.set('form');
    this.attention.reveal('student-form-title');
  }

  copyEmail() {
    const email = this.auth.user()?.institutional_email;
    if (!email) return;
    void navigator.clipboard?.writeText(email)?.catch(() => {});
    this.copiedEmail.set(true);
    if (this.copyTimer) clearTimeout(this.copyTimer);
    this.copyTimer = setTimeout(() => {
      this.copiedEmail.set(false);
      this.copyTimer = null;
    }, 2500);
  }

  prepare() {
    if (this.busy() || !this.accessId || !this.topic.trim() || !this.objective.trim()) return;
    if (this.kind === 'FEEDBACK' && !this.answer.trim()) {
      this.fail('Escribe tu respuesta para que podamos revisarla.');
      return;
    }
    this.reset();
    this.busy.set(true);
    const body = {
      access_id: this.accessId,
      topic: this.topic.trim(),
      learning_objective: this.objective.trim(),
      resource_type: this.kind,
      difficulty: this.difficulty,
      ...(this.kind === 'FEEDBACK' ? { student_answer: this.answer.trim() } : {}),
      ...(this.kind === 'QUIZ' ? { question_count: this.questionCount } : {}),
    };
    this.http
      .post<PreparationResponse>('/api/v1/learning/prepare', body)
      .pipe(
        takeUntilDestroyed(this.destroy),
        finalize(() => this.busy.set(false)),
      )
      .subscribe({
        next: (p) => {
          this.prepared.set(p);
          this.openedStatus.set('prepared');
          this.activeView.set('detail');
          this.loadHistory();
          this.attention.reveal('student-sources');
        },
        error: (e) => this.fail(this.errorText(e)),
      });
  }

  generate() {
    const p = this.prepared(),
      q = this.quota();
    if (this.busy() || this.sent() || !p || !q?.enabled || q.remaining < 1) return;
    this.busy.set(true);
    this.sent.set(true);
    this.openedStatus.set('generating');
    this.error.set('');
    this.message.set('Generando tu contenido. Puede tardar un momento…');
    this.http
      .post<GenerationResponse>(`/api/v1/learning/${p.id}/generate`, {})
      .pipe(
        takeUntilDestroyed(this.destroy),
        finalize(() => {
          this.busy.set(false);
          this.loadQuota();
          this.loadHistory();
        }),
      )
      .subscribe({
        next: (r) => {
          this.resource.set(r.resource);
          this.openedStatus.set(r.status);
          this.message.set(r.message ?? 'Tu contenido está listo y guardado en el historial.');
          this.attention.reveal('student-result');
        },
        error: (e) => {
          this.message.set(
            'Consulta el historial antes de intentarlo otra vez; no repetimos el envío automáticamente.',
          );
          this.fail(this.errorText(e));
        },
      });
  }

  open(id: string) {
    if (this.busy()) return;
    this.reset();
    this.busy.set(true);
    this.http
      .get<HistoryDetail>('/api/v1/learning/history/' + id)
      .pipe(
        takeUntilDestroyed(this.destroy),
        finalize(() => this.busy.set(false)),
      )
      .subscribe({
        next: (d) => {
          this.prepared.set(d.preparation);
          this.resource.set(d.resource);
          this.sent.set(d.status !== 'prepared');
          this.openedStatus.set(d.status);
          this.message.set(d.message ?? this.statuses[d.status]);
          this.activeView.set('detail');
          this.attention.reveal('student-sources');
        },
        error: (e) => this.fail(this.errorText(e)),
      });
  }

  typeLabel(kind: ResourceType) {
    return this.types.find((t) => t.value === kind)?.label ?? kind;
  }

  private fail(text: string) {
    this.error.set(text);
    this.attention.reveal('student-error');
  }

  private errorText(e: HttpErrorResponse) {
    return typeof e.error?.detail === 'string'
      ? e.error.detail
      : 'No se pudo completar la solicitud. Revisa los datos y vuelve a intentarlo.';
  }
}
