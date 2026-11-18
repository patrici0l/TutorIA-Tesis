import { TestBed } from '@angular/core/testing';
import { ResourceViewComponent } from './recurso';

describe('Recurso generado', () => {
  it.each(['EXERCISE', 'QUIZ', 'FEEDBACK'])('presenta el contrato %s y sus citas', async (kind) => {
    const fixture = TestBed.createComponent(ResourceViewComponent);
    const block = (text: string) => ({ text, citations: ['S1'] });
    const resources = {
      EXERCISE: {
        resource_type: 'EXERCISE',
        title: 'Práctica sintética',
        statement: block('Deriva x²'),
        hints: [block('Reconoce la tasa de cambio')],
        solution_steps: [block('Aplica la regla')],
        answer: block('2x'),
      },
      QUIZ: {
        resource_type: 'QUIZ',
        title: 'Quiz sintético',
        questions: [
          {
            statement: block('¿Cuál es la derivada?'),
            options: ['x', '2x', 'x²', '2'],
            correct_option: 1,
            explanation: block('La derivada de x² es 2x'),
          },
        ],
      },
      FEEDBACK: {
        resource_type: 'FEEDBACK',
        title: 'Revisión sintética',
        diagnosis: block('Revisa el coeficiente'),
        correction: block('La derivada es 2x'),
        next_step: block('Comprueba la regla con otro ejemplo'),
      },
    };
    fixture.componentRef.setInput('resource', resources[kind as keyof typeof resources]);
    fixture.detectChanges();
    await fixture.whenStable();
    const content = fixture.nativeElement.textContent;
    expect(content).toContain('2x');
    expect(content).toContain('Fuentes: S1');
    if (kind === 'QUIZ') {
      expect(fixture.nativeElement.querySelectorAll('input[type=radio]').length).toBe(4);
      expect(content).not.toContain('Respuesta: 2x');
      expect(fixture.nativeElement.querySelector('.quiz-review')).toBeNull();
      const option = fixture.nativeElement.querySelectorAll('input[type=radio]')[1];
      option.checked = true;
      option.dispatchEvent(new Event('change'));
      fixture.detectChanges();
      fixture.nativeElement.querySelector('.quiz-primary').click();
      fixture.detectChanges();
      expect(fixture.nativeElement.textContent).toContain('1 de 1 respuestas correctas');
      expect(fixture.nativeElement.textContent).toContain('Respuesta: 2x');
    }
    if (kind === 'FEEDBACK') expect(content).toContain('Comprueba la regla');
  });
  it('exige responder cada pregunta, conserva elecciones al volver y reinicia al cambiar de recurso', () => {
    const f = TestBed.createComponent(ResourceViewComponent);
    const question = {
      statement: { text: 'Selecciona', citations: ['S1'] },
      options: ['A', 'B', 'C', 'D'],
      correct_option: 1,
      explanation: { text: 'Explicación reservada', citations: ['S1'] },
    };
    f.componentRef.setInput('resource', {
      resource_type: 'QUIZ',
      title: 'Quiz',
      questions: [question, question],
    });
    f.detectChanges();
    const c = f.componentInstance;
    c.nextQuiz();
    expect(c.quizIndex()).toBe(0);
    expect(f.nativeElement.textContent).not.toContain('Explicación reservada');
    expect(f.nativeElement.querySelector('.quiz-toolbar button')).toBeNull();
    c.chooseQuiz(0, 0);
    c.nextQuiz();
    expect(c.quizIndex()).toBe(1);
    c.nextQuiz();
    expect(c.quizSubmitted()).toBe(false);
    c.quizIndex.set(0);
    expect(c.quizAnswers()[0]).toBe(0);
    c.nextQuiz();
    c.chooseQuiz(1, 1);
    c.nextQuiz();
    f.detectChanges();
    expect(c.quizScore()).toBe(1);
    expect(f.nativeElement.textContent).toContain('Explicación reservada');
    c.chooseQuiz(0, 1);
    expect(c.quizAnswers()[0]).toBe(0);
    f.componentRef.setInput('resource', {
      resource_type: 'QUIZ',
      title: 'Otro quiz',
      questions: [question],
    });
    f.detectChanges();
    expect(c.quizAnswers()).toEqual({});
    expect(c.quizSubmitted()).toBe(false);
    expect(c.quizIndex()).toBe(0);
    expect(f.nativeElement.textContent).not.toContain('Explicación reservada');
  });
  it('renderiza texto y citas sin activar HTML', async () => {
    const fixture = TestBed.createComponent(ResourceViewComponent);
    const block = { text: '<script>no ejecutar</script>', citations: ['S1'] };
    fixture.componentRef.setInput('resource', {
      resource_type: 'EXPLANATION',
      title: 'Explicación',
      summary: block,
      steps: [block],
      worked_example: block,
    });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain(block.text);
    expect(fixture.nativeElement.textContent).toContain('Fuentes: S1');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
  });
  it('presenta fórmulas en el quiz y reemplaza el recurso sin conservar ecuaciones anteriores', () => {
    const fixture = TestBed.createComponent(ResourceViewComponent);
    fixture.componentRef.setInput('resource', {
      resource_type: 'QUIZ',
      title: 'Integrales',
      questions: [
        {
          statement: { text: String.raw`Calcula $\int_0^1 x dx$`, citations: ['S1'] },
          options: [String.raw`$\frac{1}{2}$`, '1', '2', '0'],
          correct_option: 0,
          explanation: { text: String.raw`Resultado: \(\frac{1}{2}\)`, citations: ['S1'] },
        },
      ],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('.katex').length).toBe(2);
    expect(fixture.nativeElement.textContent).toContain('Fuentes: S1');
    const block = { text: 'Nuevo recurso sin fórmulas', citations: ['S2'] };
    fixture.componentRef.setInput('resource', {
      resource_type: 'EXPLANATION',
      title: 'Concepto',
      summary: block,
      steps: [],
      worked_example: block,
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.katex')).toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain('Integrales');
  });
});
