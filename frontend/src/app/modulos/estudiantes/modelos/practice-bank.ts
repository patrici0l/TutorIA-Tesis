import { PRACTICE_QUESTIONS, PracticeQuestion } from './practice-question';
import { RULES_QUESTIONS } from './practice-rules';

export const PRACTICE_BANKS: readonly {
  version: string;
  title: string;
  questions: readonly PracticeQuestion[];
}[] = [
  { version: 'derivadas-v1', title: 'Fundamentos de derivadas', questions: PRACTICE_QUESTIONS },
  { version: 'reglas-v1', title: 'Cadena, producto y cociente', questions: RULES_QUESTIONS },
];
