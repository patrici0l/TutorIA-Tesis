import { ViewAttention } from '../atencion-vista.service';
// Presenta cada contrato de recurso conservando fuentes y soluciones disponibles.
import { MathTextDirective } from '../texto-matematico.directive';
import {
  Component,
  computed,
  inject,
  input,
  OnChanges,
  signal,
  SimpleChanges,
} from '@angular/core';
import { CitedText, EducationalResource } from './recursos.model';

@Component({
  imports: [MathTextDirective],
  selector: 'app-resource-view',
  host: { '[class.compact]': 'compact()' },
  templateUrl: './recurso.html',
  styleUrls: ['./recurso.scss', './quiz.scss'],
})
export class ResourceViewComponent implements OnChanges {
  private readonly attention = inject(ViewAttention);
  readonly compact = input(false);
  readonly resource = input.required<EducationalResource>();
  readonly teacherView = input(false);
  readonly quizIndex = signal(0);
  readonly quizAnswers = signal<Record<number, number>>({});
  readonly quizSubmitted = signal(false);
  readonly solutionsVisible = signal(false);
  readonly quizId = crypto.randomUUID();
  readonly quizQuestions = computed(() => {
    const resource = this.resource();
    return resource.resource_type === 'QUIZ' ? resource.questions : [];
  });
  readonly quizScore = computed(
    () =>
      this.quizQuestions().filter(
        (question, index) => this.quizAnswers()[index] === question.correct_option,
      ).length,
  );
  ngOnChanges(changes: SimpleChanges) {
    if (changes['resource']) this.resetQuiz();
    if (changes['teacherView']) this.solutionsVisible.set(false);
  }
  resetQuiz() {
    this.quizIndex.set(0);
    this.quizAnswers.set({});
    this.quizSubmitted.set(false);
    this.solutionsVisible.set(false);
  }
  chooseQuiz(question: number, option: number) {
    const item = this.quizQuestions()[question];
    if (
      this.quizSubmitted() ||
      !item ||
      !Number.isInteger(option) ||
      option < 0 ||
      option >= item.options.length
    )
      return;
    this.quizAnswers.update((answers) => ({ ...answers, [question]: option }));
  }
  nextQuiz() {
    if (this.quizAnswers()[this.quizIndex()] === undefined || this.quizSubmitted()) return;
    if (this.quizIndex() < this.quizQuestions().length - 1) {
      this.quizIndex.update((index) => index + 1);
      this.attention.reveal(this.quizId + '-question');
    } else if (this.quizQuestions().every((_, index) => this.quizAnswers()[index] !== undefined)) {
      this.quizSubmitted.set(true);
      this.attention.reveal(this.quizId + '-result');
    }
  }
  sections(): { heading: string; blocks: CitedText[] }[] {
    const r = this.resource();
    switch (r.resource_type) {
      case 'EXPLANATION':
        return [
          { heading: 'Concepto', blocks: [r.summary] },
          { heading: 'Paso a paso', blocks: r.steps },
          { heading: 'Ejemplo resuelto', blocks: [r.worked_example] },
        ];
      case 'EXAMPLE':
        return [
          { heading: 'Enunciado', blocks: [r.statement] },
          { heading: 'Solución paso a paso', blocks: r.solution_steps },
          { heading: 'Resultado', blocks: [r.answer] },
        ];
      case 'HINT':
        return [
          { heading: 'Enunciado', blocks: [r.statement] },
          { heading: 'Pistas para continuar', blocks: r.hints },
        ];
      case 'EXERCISE':
        return [
          { heading: 'Enunciado', blocks: [r.statement] },
          { heading: 'Pistas', blocks: r.hints },
          { heading: 'Solución guiada', blocks: r.solution_steps },
          { heading: 'Resultado', blocks: [r.answer] },
        ];
      case 'FEEDBACK':
        return [
          { heading: 'Revisión', blocks: [r.diagnosis] },
          { heading: 'Corrección', blocks: [r.correction] },
          { heading: 'Siguiente paso', blocks: [r.next_step] },
        ];
      case 'QUIZ':
        return [];
    }
  }
}
