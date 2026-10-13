export interface PracticeQuestion {
  topic: string;
  statement: string;
  options: readonly string[];
  correctOption: number;
  hint: string;
  explanation: string;
  feedback: readonly string[];
}

// Actividades introductorias fijas; no son recursos generados ni evaluaciones institucionales.
export const PRACTICE_QUESTIONS: readonly PracticeQuestion[] = [
  {
    topic: 'Regla de la potencia',
    statement: 'Si f(x) = x³, ¿cuál es su derivada?',
    options: ['3x²', 'x²', '3x³', 'x⁴ / 4'],
    correctOption: 0,
    hint: 'Multiplica por el exponente y después réstale uno al exponente.',
    explanation: 'La regla es d(xⁿ)/dx = n·xⁿ⁻¹. Para n = 3, obtenemos f′(x) = 3x².',
    feedback: [
      'Aplicaste las dos partes de la regla.',
      'Reduciste el exponente, pero falta multiplicar por 3.',
      'Multiplicaste por 3, pero el exponente debe bajar de 3 a 2.',
      'Esta expresión corresponde a una primitiva, no a la derivada.',
    ],
  },
  {
    topic: 'Suma y constantes',
    statement: 'Si g(x) = 2x² + 5x − 7, ¿cuál es g′(x)?',
    options: ['4x + 5 − 7', '2x + 5', '4x + 5', '4x² + 5x'],
    correctOption: 2,
    hint: 'Deriva cada término por separado. La derivada de una constante es cero.',
    explanation:
      'La derivada de 2x² es 4x; la de 5x es 5; la de −7 es 0. Por tanto, g′(x) = 4x + 5.',
    feedback: [
      'La constante −7 desaparece al derivar: su variación es cero.',
      'Al derivar 2x² debes multiplicar también por el exponente 2.',
      'Derivaste cada término y eliminaste correctamente la constante.',
      'Al derivar una potencia, su exponente disminuye en uno.',
    ],
  },
  {
    topic: 'Pendiente en un punto',
    statement: 'Para h(x) = x², ¿cuál es la pendiente de la recta tangente cuando x = 3?',
    options: ['9', '3', '2', '6'],
    correctOption: 3,
    hint: 'Calcula primero h′(x) y luego evalúa esa derivada en x = 3.',
    explanation:
      'h′(x) = 2x. Al evaluar en x = 3, h′(3) = 2·3 = 6. La pendiente es 6; h(3) = 9 es la altura del punto.',
    feedback: [
      '9 es el valor de h(3), no la pendiente. Evalúa la derivada.',
      '3 es la coordenada x del punto; falta evaluar 2x.',
      '2 es el coeficiente de la derivada, pero aún debes sustituir x = 3.',
      'Distinguiste el valor de la función de su tasa de cambio.',
    ],
  },
];
