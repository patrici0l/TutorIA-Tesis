import { PracticeQuestion } from './practice-question';

export const RULES_QUESTIONS: readonly PracticeQuestion[] = [
  {
    topic: 'Regla de la cadena',
    statement: 'Si f(x) = (2x + 1)³, ¿cuál es f′(x)?',
    options: ['3(2x + 1)²', '6(2x + 1)²', '6(2x + 1)³', '(2x + 1)²'],
    correctOption: 1,
    hint: 'Deriva la potencia y multiplica por la derivada de 2x + 1.',
    explanation: 'Con u = 2x + 1, la derivada de u³ es 3u²·u′. Como u′ = 2, f′(x) = 6(2x + 1)².',
    feedback: [
      'Falta multiplicar por la derivada interna, que es 2.',
      'Aplicaste la derivada externa y la interna.',
      'El exponente debe disminuir de 3 a 2.',
      'Faltan el factor 3 de la potencia y el factor 2 de la función interna.',
    ],
  },
  {
    topic: 'Regla del producto',
    statement: 'Si g(x) = x²(x + 1), ¿cuál es g′(x)?',
    options: ['3x² + 2x', '2x', '2x(x + 1)', '3x² + 1'],
    correctOption: 0,
    hint: 'Usa (uv)′ = u′v + uv′. También puedes expandir el producto primero.',
    explanation:
      'g′(x) = 2x(x + 1) + x²·1 = 3x² + 2x. Expandir g(x) = x³ + x² conduce al mismo resultado.',
    feedback: [
      'Sumaste las dos contribuciones del producto.',
      'La derivada del producto no es el producto de las derivadas.',
      'Falta sumar x² por la derivada del segundo factor.',
      'La derivada de x² es 2x, no 1.',
    ],
  },
  {
    topic: 'Regla del cociente',
    statement: 'Si h(x) = x / (x + 1), con x ≠ −1, ¿cuál es h′(x)?',
    options: ['1', '−1 / (x + 1)²', '1 / (x + 1)²', '1 / (x + 1)'],
    correctOption: 2,
    hint: 'Usa (u/v)′ = (u′v − uv′) / v².',
    explanation:
      'h′(x) = ((x + 1) − x) / (x + 1)² = 1 / (x + 1)². Se mantiene la restricción x ≠ −1.',
    feedback: [
      'La derivada de un cociente no es el cociente de las derivadas.',
      'El orden del numerador es u′v − uv′, que aquí da 1.',
      'Calculaste el numerador y elevaste el denominador al cuadrado.',
      'El denominador de la regla debe elevarse al cuadrado.',
    ],
  },
];
