// Gestiona respuestas e intentos; la corrección persistida la calcula el servidor.
import { MathTextDirective } from '../../compartido/texto-matematico.directive';
import {
  afterNextRender, Component, computed, DestroyRef, ElementRef, HostListener,
  inject, Injector, Input, OnInit, signal, viewChild,
} from '@angular/core';
import { Assignment } from '../../compartido/actividades/actividades.model';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  PracticeProgress,
  PracticeResult,
  PracticeService,
  PRACTICE_VERSION,
} from './practica.service';
import { ViewAttention } from '../../compartido/atencion-vista.service';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { PRACTICE_BANKS } from '../../compartido/practica/bancos';
import { PracticeExitService } from '../../compartido/practica/salida-practica.service';

@Component({
  selector: 'app-practice',
  imports: [MathTextDirective, RouterLink, DatePipe],
  templateUrl: './practica.html',
  styleUrls: ['./practica.scss', './compacto.scss'],
})
export class PracticeComponent implements OnInit {
  private readonly attention = inject(ViewAttention);
  private readonly injector = inject(Injector);
  private readonly exit = inject(PracticeExitService);
  private readonly pendingDialog = viewChild<ElementRef<HTMLDialogElement>>('pendingDialog');
  private pendingDecision: Promise<boolean> | null = null;
  private resolveDecision: ((confirmed: boolean) => void) | null = null;
  private decisionTrigger: HTMLElement | null = null;
  private leaveApproved = false;
  readonly pendingAction = signal<'restart' | 'leave' | null>(null);
  private readonly route = inject(ActivatedRoute);
  readonly activeView = signal<'practice' | 'history'>(
    this.route.snapshot?.fragment === 'history-title' ? 'history' : 'practice',
  );
  showHistory() {
    this.activeView.set('history');
    this.attention.reveal('history-title');
  }
  openReview(attempt: PracticeResult) {
    this.activeView.set('history');
    this.reviewing.set(attempt);
    this.attention.reveal('review-title');
  }
  closeReview() {
    this.reviewing.set(null);
    this.attention.reveal('history-title');
  }
  @Input() assignment: Assignment | null = null;
  private readonly service = inject(PracticeService);
  private readonly destroyRef = inject(DestroyRef);
  private attemptId = crypto.randomUUID();
  readonly saving = signal(false);
  readonly saved = signal<PracticeResult | null>(null);
  readonly saveError = signal('');
  readonly historyLoading = signal(false);
  readonly historyError = signal(false);
  readonly history = signal<PracticeProgress | null>(null);
  readonly reviewing = signal<PracticeResult | null>(null);
  readonly banks = PRACTICE_BANKS;
  readonly version = signal(PRACTICE_VERSION);
  readonly reviewBank = computed(() =>
    this.banks.find((bank) => bank.version === this.reviewing()?.version),
  );
  get questions() {
    return this.banks.find((bank) => bank.version === this.version())!.questions;
  }
  bankTitle(version: string) {
    return this.banks.find((bank) => bank.version === version)?.title ?? 'Práctica anterior';
  }
  selectBank(version: string) {
    if (
      this.assignment ||
      this.saving() ||
      this.selected() !== null ||
      this.answers().length ||
      !this.banks.some((bank) => bank.version === version)
    )
      return;
    this.restart();
    this.version.set(version);
  }
  readonly reviewAvailable = computed(() => {
    const attempt = this.reviewing();
    return (
      !!attempt &&
      !!this.reviewBank() &&
      attempt.answers.length === this.reviewBank()!.questions.length &&
      attempt.answers.every(
        (answer, i) =>
          Number.isInteger(answer) &&
          answer >= 0 &&
          answer < this.reviewBank()!.questions[i].options.length,
      )
    );
  });
  readonly reviewTopics = computed(() =>
    this.reviewAvailable()
      ? this.reviewBank()!
          .questions.filter((item, i) => this.reviewing()!.answers[i] !== item.correctOption)
          .map((item) => item.topic)
      : [],
  );
  readonly index = signal(0);
  readonly selected = signal<number | null>(null);
  readonly submitted = signal(false);
  readonly hintVisible = signal(false);
  readonly answers = signal<number[]>([]);
  readonly complete = signal(false);
  readonly hasPendingResult = computed(() =>
    !this.saved() && (this.answers().length > 0 || this.saving()),
  );
  readonly question = computed(() => this.questions[this.index()]);
  readonly correct = computed(() => this.selected() === this.question().correctOption);
  readonly score = computed(
    () => this.answers().filter((answer, i) => answer === this.questions[i].correctOption).length,
  );

  ngOnInit() {
    if (this.assignment) this.version.set(this.assignment.version);
    const unregister = this.exit.register(() => this.canLeavePractice());
    this.destroyRef.onDestroy(() => {
      unregister();
      this.finishDecision(false, false);
    });
    this.loadHistory();
  }

  @HostListener('window:beforeunload', ['$event'])
  beforeUnload(event: BeforeUnloadEvent) {
    if (!this.hasPendingResult() || this.leaveApproved) return;
    event.preventDefault();
    event.returnValue = '';
  }

  canLeavePractice(): boolean | Promise<boolean> {
    if (!this.hasPendingResult() || this.leaveApproved) return true;
    return this.askBeforeLosingResult('leave');
  }

  private askBeforeLosingResult(action: 'restart' | 'leave'): Promise<boolean> {
    if (this.pendingDecision) return this.pendingDecision;
    this.decisionTrigger = document.activeElement instanceof HTMLElement
      ? document.activeElement : null;
    this.pendingAction.set(action);
    this.pendingDecision = new Promise((resolve) => { this.resolveDecision = resolve; });
    afterNextRender(() => this.pendingDialog()?.nativeElement.showModal(), {
      injector: this.injector,
    });
    this.attention.reveal('pending-practice-title');
    return this.pendingDecision;
  }

  cancelPending() {
    if (!this.saving()) this.finishDecision(false);
  }

  discardPending() {
    if (this.saving()) return;
    this.leaveApproved = this.pendingAction() === 'leave';
    this.finishDecision(true);
  }

  savePending() {
    if (this.complete()) this.saveResult();
  }

  private finishDecision(confirmed: boolean, restoreFocus = true) {
    const resolve = this.resolveDecision;
    this.resolveDecision = null;
    this.pendingDecision = null;
    this.pendingAction.set(null);
    const dialog = this.pendingDialog()?.nativeElement;
    if (dialog?.open) dialog.close();
    if (!confirmed && restoreFocus) this.decisionTrigger?.focus();
    this.decisionTrigger = null;
    resolve?.(confirmed);
  }

  loadHistory(offset = 0) {
    if (this.historyLoading()) return;
    this.historyLoading.set(true);
    this.historyError.set(false);
    this.service
      .progress(offset)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (page) => {
          this.history.set(page);
          this.historyLoading.set(false);
        },
        error: () => {
          this.historyError.set(true);
          this.historyLoading.set(false);
        },
      });
  }

  saveResult() {
    if (!this.complete() || this.saving() || this.saved()) return;
    this.saving.set(true);
    this.saveError.set('');
    this.service
      .save(this.attemptId, this.answers(), this.version(), this.assignment?.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (result) => {
          this.saved.set(result);
          this.saving.set(false);
          this.loadHistory();
          if (this.pendingAction()) this.finishDecision(true);
        },
        error: (error) => {
          this.saving.set(false);
          this.saveError.set(
            error.status === 409 && typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No pudimos confirmar el guardado. Vuelve a intentarlo antes de salir; no se duplicará este intento.',
          );
        },
      });
  }

  choose(option: number) {
    this.leaveApproved = false;
    if (
      !this.submitted() &&
      Number.isInteger(option) &&
      option >= 0 &&
      option < this.question().options.length
    )
      this.selected.set(option);
  }
  check() {
    const answer = this.selected();
    if (answer === null || this.submitted() || this.complete()) return;
    this.submitted.set(true);
    this.answers.update((answers) => [...answers, answer]);
    this.attention.reveal('practice-feedback');
  }
  next() {
    if (!this.submitted()) return;
    if (this.index() === this.questions.length - 1) {
      this.complete.set(true);
      this.attention.reveal('result-title');
      return;
    }
    this.index.update((index) => index + 1);
    this.selected.set(null);
    this.submitted.set(false);
    this.hintVisible.set(false);
    this.attention.reveal('question-title');
  }
  async restart() {
    if (this.saving()) return;
    if (this.hasPendingResult() && !(await this.askBeforeLosingResult('restart'))) return;
    this.leaveApproved = false;
    this.activeView.set('practice');
    this.reviewing.set(null);
    this.attemptId = crypto.randomUUID();
    this.saved.set(null);
    this.saveError.set('');
    this.index.set(0);
    this.selected.set(null);
    this.submitted.set(false);
    this.hintVisible.set(false);
    this.answers.set([]);
    this.complete.set(false);
    this.attention.reveal('question-title');
  }
}
