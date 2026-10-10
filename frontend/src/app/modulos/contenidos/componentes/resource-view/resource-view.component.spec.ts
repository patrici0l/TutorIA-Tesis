import { TestBed } from '@angular/core/testing';
import { ResourceViewComponent } from './resource-view.component';

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
      expect(fixture.nativeElement.querySelectorAll('li').length).toBe(4);
      expect(content).toContain('Respuesta: 2x');
      expect(fixture.nativeElement.querySelector('details')).not.toBeNull();
    }
    if (kind === 'FEEDBACK') expect(content).toContain('Comprueba la regla');
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
});
