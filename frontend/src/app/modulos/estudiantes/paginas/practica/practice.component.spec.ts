import { of, Subject, throwError } from 'rxjs';
import { PracticeService, PracticeResult } from '../../servicios/practice.service';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { PracticeComponent } from './practice.component';

describe('Práctica del estudiante', () => {
  const service = { progress: vi.fn(), save: vi.fn() };
  it('explica el cierre durante una práctica sin perder las respuestas del alumno', async () => {
    const f = TestBed.createComponent(PracticeComponent);
    f.componentRef.setInput('assignment', { id: 'assigned', version: 'reglas-v1', status: 'open' });
    await f.whenStable();
    const c = f.componentInstance;
    for (const answer of [1, 0, 2]) {
      c.choose(answer);
      c.check();
      c.next();
    }
    service.save.mockReturnValue(
      throwError(() => ({
        status: 409,
        error: { detail: 'La actividad está cerrada o cancelada y no admite nuevos intentos.' },
      })),
    );
    c.saveResult();
    await f.whenStable();
    expect(f.nativeElement.textContent).toContain('no admite nuevos intentos');
    expect(c.answers()).toEqual([1, 0, 2]);
    expect(c.saved()).toBeNull();
  });
  it('fija el bloque asignado y envía la actividad al guardar', async () => {
    const f = TestBed.createComponent(PracticeComponent);
    f.componentRef.setInput('assignment', { id: 'assigned', version: 'reglas-v1' });
    await f.whenStable();
    const c = f.componentInstance;
    c.selectBank('derivadas-v1');
    expect(c.version()).toBe('reglas-v1');
    expect(f.nativeElement.querySelector('#bank-title')).toBeNull();
    for (const answer of [1, 0, 2]) {
      c.choose(answer);
      c.check();
      c.next();
    }
    service.save.mockReturnValue(of({ score: 3 }));
    c.saveResult();
    expect(service.save.mock.calls[0].slice(1)).toEqual([[1, 0, 2], 'reglas-v1', 'assigned']);
  });
  it('cambia de bloque antes de responder, guarda su versión y revisa el banco original', async () => {
    const fixture = TestBed.createComponent(PracticeComponent);
    await fixture.whenStable();
    const c = fixture.componentInstance;
    c.selectBank('reglas-v1');
    c.choose(1);
    c.selectBank('derivadas-v1');
    expect(c.version()).toBe('reglas-v1');
    c.check();
    c.next();
    for (const answer of [0, 2]) {
      c.choose(answer);
      c.check();
      c.next();
    }
    expect(c.score()).toBe(3);
    service.save.mockReturnValue(
      of({
        id: 'rules',
        version: 'reglas-v1',
        answers: [1, 0, 2],
        score: 3,
        created_at: '2026-10-14T12:00:00Z',
      }),
    );
    c.saveResult();
    expect(service.save.mock.calls[0][2]).toBe('reglas-v1');
    c.reviewing.set({
      id: 'old',
      version: 'derivadas-v1',
      answers: [0, 2, 3],
      score: 3,
      created_at: '2026-10-13T12:00:00Z',
    });
    await fixture.whenStable();
    const review = fixture.nativeElement.querySelector('#attempt-review');
    expect(review.textContent).toContain('Regla de la potencia');
    expect(review.textContent).not.toContain('Regla de la cadena');
    c.restart();
    c.selectBank('derivadas-v1');
    expect(c.questions[0].topic).toBe('Regla de la potencia');
  });
  beforeEach(async () => {
    service.progress
      .mockReset()
      .mockReturnValue(of({ items: [], total: 0, best_score: null, offset: 0, limit: 10 }));
    service.save.mockReset();
    await TestBed.configureTestingModule({
      imports: [PracticeComponent],
      providers: [provideRouter([]), { provide: PracticeService, useValue: service }],
    }).compileComponents();
  });
  it('requiere respuesta y permite consultar una pista', async () => {
    const fixture = TestBed.createComponent(PracticeComponent);
    await fixture.whenStable();
    const component = fixture.componentInstance;
    component.check();
    component.next();
    expect(component.index()).toBe(0);
    expect(component.answers()).toEqual([]);
    expect(
      fixture.nativeElement.querySelector('section[aria-labelledby=question-title] .buttons button')
        .disabled,
    ).toBe(true);
    fixture.nativeElement
      .querySelector('section[aria-labelledby=question-title] .secondary')
      .click();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('.hint').textContent).toContain('exponente');
  });
  it('muestra retroalimentación del error y evita modificar un intento comprobado', async () => {
    const fixture = TestBed.createComponent(PracticeComponent);
    await fixture.whenStable();
    const radio = fixture.nativeElement.querySelectorAll('input')[1] as HTMLInputElement;
    radio.click();
    await fixture.whenStable();
    fixture.nativeElement
      .querySelector('section[aria-labelledby=question-title] .buttons button')
      .click();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('.feedback').textContent).toContain(
      'falta multiplicar por 3',
    );
    fixture.componentInstance.choose(0);
    fixture.componentInstance.check();
    expect(fixture.componentInstance.answers()).toEqual([1]);
    expect(fixture.componentInstance.score()).toBe(0);
    expect(fixture.nativeElement.querySelector('progress').value).toBe(1);
  });
  it('completa una sesión, resume aciertos y reinicia sin conservar respuestas', async () => {
    const fixture = TestBed.createComponent(PracticeComponent);
    const component = fixture.componentInstance;
    for (const answer of [0, 0, 3]) {
      component.choose(answer);
      component.check();
      component.next();
    }
    await fixture.whenStable();
    expect(component.complete()).toBe(true);
    expect(component.score()).toBe(2);
    expect(fixture.nativeElement.textContent).toContain('2 de 3');
    expect(fixture.nativeElement.textContent).toContain('Para repasar');
    fixture.nativeElement
      .querySelector('section[aria-labelledby=result-title] button.secondary')
      .click();
    await fixture.whenStable();
    expect(component.answers()).toEqual([]);
    expect(component.complete()).toBe(false);
    expect(component.selected()).toBeNull();
    expect(fixture.nativeElement.querySelectorAll('input:checked').length).toBe(0);
  });

  it('reintenta guardado con el mismo identificador y bloquea duplicados y reinicio durante envío', async () => {
    const fixture = TestBed.createComponent(PracticeComponent);
    const c = fixture.componentInstance;
    for (const answer of [0, 2, 3]) {
      c.choose(answer);
      c.check();
      c.next();
    }
    service.save.mockReturnValueOnce(throwError(() => new Error('network')));
    c.saveResult();
    expect(c.saveError()).toContain('No pudimos confirmar');
    const id = service.save.mock.calls[0][0];
    const pending = new Subject<PracticeResult>();
    service.save.mockReturnValue(pending);
    c.saveResult();
    c.saveResult();
    c.restart();
    expect(service.save).toHaveBeenCalledTimes(2);
    expect(service.save.mock.calls[1][0]).toBe(id);
    expect(c.complete()).toBe(true);
    pending.next({
      id,
      version: 'derivadas-v1',
      answers: [0, 2, 3],
      score: 3,
      created_at: '2026-10-12T12:00:00Z',
    });
    pending.complete();
    expect(c.saved()?.score).toBe(3);
    c.saveResult();
    expect(service.save).toHaveBeenCalledTimes(2);
    c.restart();
    expect(c.saved()).toBeNull();
  });
  it('informa fallo al consultar historial sin impedir practicar', async () => {
    service.progress.mockReturnValue(throwError(() => new Error('offline')));
    const fixture = TestBed.createComponent(PracticeComponent);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('No pudimos cargar tu historial');
    fixture.componentInstance.choose(0);
    fixture.componentInstance.check();
    expect(fixture.componentInstance.correct()).toBe(true);
  });
  it('revisa un intento guardado sin perder la práctica en curso ni guardar otro', async () => {
    const attempt: PracticeResult = {
      id: 'history-1',
      version: 'derivadas-v1',
      answers: [1, 2, 3],
      score: 2,
      created_at: '2026-10-13T12:00:00Z',
    };
    service.progress.mockReturnValue(
      of({ items: [attempt], total: 1, best_score: 2, offset: 0, limit: 10 }),
    );
    const fixture = TestBed.createComponent(PracticeComponent);
    await fixture.whenStable();
    const c = fixture.componentInstance;
    c.choose(2);
    fixture.nativeElement.querySelector('.review-button').click();
    await fixture.whenStable();
    const review = fixture.nativeElement.querySelector('#attempt-review');
    expect(review.textContent).toContain('falta multiplicar por 3');
    expect(review.textContent).toContain('Conceptos para reforzar: Regla de la potencia');
    expect(review.querySelectorAll('.feedback.correct').length).toBe(2);
    expect(c.selected()).toBe(2);
    expect(c.answers()).toEqual([]);
    expect(service.save).not.toHaveBeenCalled();
    review.querySelector('button').click();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('#attempt-review')).toBeNull();
    expect(c.selected()).toBe(2);
  });
  it.each([
    ['derivadas-v2', [0, 2, 3]],
    ['derivadas-v1', [0, 2]],
    ['derivadas-v1', [0, 2, 9]],
  ])('no interpreta respuestas incompatibles: %s %s', async (version, answers) => {
    const fixture = TestBed.createComponent(PracticeComponent);
    fixture.componentInstance.reviewing.set({
      id: 'old',
      version: version as string,
      answers: answers as number[],
      score: 2,
      created_at: '2026-10-13T12:00:00Z',
    });
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('#attempt-review').textContent).toContain(
      'No está disponible el detalle',
    );
    expect(fixture.nativeElement.querySelector('.review-list')).toBeNull();
  });
});
