// Gestiona respuestas e intentos; la corrección persistida la calcula el servidor.
import { MathTextDirective } from '../../compartido/texto-matematico.directive';
import { Component, computed, DestroyRef, inject, Input, OnInit, signal } from '@angular/core';
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

@Component({
  selector: 'app-practice',
  imports: [MathTextDirective, RouterLink, DatePipe],
  templateUrl: './practica.html',
  styleUrls: ['./practica.scss', './compacto.scss'],
})
export class PracticeComponent implements OnInit {
  private readonly attention = inject(ViewAttention);
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
  readonly question = computed(() => this.questions[this.index()]);
  readonly correct = computed(() => this.selected() === this.question().correctOption);
  readonly score = computed(
    () => this.answers().filter((answer, i) => answer === this.questions[i].correctOption).length,
  );

  ngOnInit() {
    if (this.assignment) this.version.set(this.assignment.version);
    this.loadHistory();
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
  }
  next() {
    if (!this.submitted()) return;
    if (this.index() === this.questions.length - 1) {
      this.complete.set(true);
      return;
    }
    this.index.update((index) => index + 1);
    this.selected.set(null);
    this.submitted.set(false);
    this.hintVisible.set(false);
  }
  restart() {
    if (this.saving()) return;
    this.attemptId = crypto.randomUUID();
    this.saved.set(null);
    this.saveError.set('');
    this.index.set(0);
    this.selected.set(null);
    this.submitted.set(false);
    this.hintVisible.set(false);
    this.answers.set([]);
    this.complete.set(false);
  }
}
