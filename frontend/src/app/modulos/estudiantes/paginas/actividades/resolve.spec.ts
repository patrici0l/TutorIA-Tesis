import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { BehaviorSubject, of, throwError } from 'rxjs';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { AssignmentService } from '../../servicios/assignment.service';
import { PracticeService } from '../../servicios/practice.service';
import { AssignmentPracticeComponent } from './resolve';

describe('Resolver actividad', () => {
  it('muestra el recurso asignado con fuentes, sin sustituirlo por derivadas ni registrar notas', async () => {
    const block = { text: 'La integral de 2x es x² + C.', citations: ['S1'] };
    const resource = {
      resource_type: 'EXPLANATION',
      title: 'Integrales',
      summary: block,
      steps: [block],
      worked_example: block,
    };
    const progress = vi.fn();
    await TestBed.configureTestingModule({
      imports: [AssignmentPracticeComponent],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ id: 'integrales' })) },
        },
        { provide: AuthService, useValue: { user: signal({ rol: 'student' }) } },
        { provide: PracticeService, useValue: { progress } },
        {
          provide: AssignmentService,
          useValue: {
            detail: () =>
              of({
                id: 'integrales',
                title: 'Repaso de integrales',
                version: 'resource-v1',
                resource_id: 'r1',
                status: 'open',
                resource,
                sources: [
                  {
                    citation_id: 'S1',
                    document_title: 'Cálculo integral',
                    source_kind: 'page',
                    source_index: 2,
                    text: 'Antiderivadas',
                  },
                ],
              }),
          },
        },
      ],
    }).compileComponents();
    const f = TestBed.createComponent(AssignmentPracticeComponent);
    await f.whenStable();
    expect(f.nativeElement.textContent).toContain('La integral de 2x es x² + C.');
    expect(f.nativeElement.textContent).toContain('Cálculo integral');
    expect(f.nativeElement.textContent).toContain('no registra una calificación');
    expect(f.nativeElement.querySelector('app-practice')).toBeNull();
    expect(progress).not.toHaveBeenCalled();
  });
  it('reinicia el ejercicio al navegar a otra actividad y bloquea una inaccesible', async () => {
    const params = new BehaviorSubject(convertToParamMap({ id: 'first' }));
    const detail = vi.fn().mockImplementation((id: string) =>
      id === 'missing'
        ? throwError(() => new Error('404'))
        : of({
            id,
            version: id === 'first' ? 'reglas-v1' : 'derivadas-v1',
            title: id,
            instructions: '',
            status: id === 'closed' || id === 'cancelled' ? id : 'open',
            attempts: 1,
            best_score: 3,
          }),
    );
    await TestBed.configureTestingModule({
      imports: [AssignmentPracticeComponent],
      providers: [
        provideRouter([]),
        { provide: ActivatedRoute, useValue: { paramMap: params } },
        { provide: AuthService, useValue: { user: signal({ rol: 'student' }) } },
        { provide: AssignmentService, useValue: { detail } },
        {
          provide: PracticeService,
          useValue: {
            progress: () => of({ items: [], total: 0, best_score: null, offset: 0, limit: 10 }),
          },
        },
      ],
    }).compileComponents();
    const f = TestBed.createComponent(AssignmentPracticeComponent);
    await f.whenStable();
    expect(f.nativeElement.textContent).toContain('(2x + 1)³');
    params.next(convertToParamMap({ id: 'second' }));
    await f.whenStable();
    expect(f.nativeElement.textContent).toContain('Si f(x) = x³');
    expect(f.nativeElement.querySelectorAll('input:checked').length).toBe(0);
    for (const status of ['closed', 'cancelled']) {
      params.next(convertToParamMap({ id: status }));
      await f.whenStable();
      expect(f.nativeElement.querySelector('app-practice')).toBeNull();
      expect(f.nativeElement.textContent).toContain('no admite nuevos intentos');
      expect(f.nativeElement.textContent).toContain('Mejor resultado: 3 de 3');
      expect(f.nativeElement.querySelector('a[href="/practica#history-title"]')).not.toBeNull();
    }
    params.next(convertToParamMap({ id: 'missing' }));
    await f.whenStable();
    expect(f.nativeElement.querySelector('app-practice')).toBeNull();
    expect(f.nativeElement.querySelector('[role=alert]').textContent).toContain(
      'no está disponible',
    );
  });
});
