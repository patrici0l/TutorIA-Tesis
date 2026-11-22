import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from '../inicio/sesion.service';
import { StudentContentComponent } from './solicitar';

describe('Solicitudes del estudiante', () => {
  const user = signal({ rol: 'student', institutional_email: 'estudiante@est.ups.edu.ec' });
  let http: HttpTestingController;
  beforeEach(() => {
    user.set({ rol: 'student', institutional_email: 'estudiante@est.ups.edu.ec' });
    TestBed.configureTestingModule({
      imports: [StudentContentComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user, mode: signal('mock') } },
      ],
    });
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  function setup(courses = [{ id: 'access', course: 'cálculo', teacher: 'Profesor' }]) {
    const f = TestBed.createComponent(StudentContentComponent);
    http.expectOne('/api/v1/learning/courses').flush(courses);
    http.expectOne('/api/v1/learning/quota').flush({ enabled: true, remaining: 3 });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0, offset: 0, limit: 10 });
    return f;
  }
  it('exige respuesta para feedback y no envía materia, docente o perfil elegidos por cliente', () => {
    const c = setup().componentInstance;
    c.accessId = 'access';
    c.topic = 'Derivadas';
    c.objective = 'Revisar mis pasos';
    c.kind = 'FEEDBACK';
    c.prepare();
    http.expectNone('/api/v1/learning/prepare');
    expect(c.error()).toContain('Escribe tu respuesta');
    c.answer = 'Mi respuesta';
    c.prepare();
    c.prepare();
    const req = http.expectOne('/api/v1/learning/prepare');
    expect(req.request.body).toEqual({
      access_id: 'access',
      topic: 'Derivadas',
      learning_objective: 'Revisar mis pasos',
      resource_type: 'FEEDBACK',
      difficulty: 'basic',
      student_answer: 'Mi respuesta',
    });
    req.flush({ detail: 'No tienes acceso a esta asignatura.' }, { status: 403, statusText: 'Forbidden' });
    expect(c.busy()).toBe(false);
    expect(c.error()).toContain('No tienes acceso');
  });
  it('preparar no genera y bloquea un segundo envío mientras guarda el resultado', () => {
    const c = setup().componentInstance;
    c.accessId = 'access';
    c.topic = 'Derivadas';
    c.objective = 'Entender la regla';
    c.prepare();
    http.expectOne('/api/v1/learning/prepare').flush({ id: 'preparation', sources: [] });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0 });
    http.expectNone('/api/v1/learning/preparation/generate');
    c.generate();
    c.generate();
    http
      .expectOne('/api/v1/learning/preparation/generate')
      .flush({ status: 'failed', resource: null, message: 'Respuesta inválida.' });
    http.expectOne('/api/v1/learning/quota').flush({ enabled: true, remaining: 2 });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0 });
    c.generate();
    http.expectNone('/api/v1/learning/preparation/generate');
    expect(c.message()).toBe('Respuesta inválida.');
  });
  it('no consulta datos del estudiante con una sesión docente', () => {
    user.set({ rol: 'teacher', institutional_email: 'docente@ups.edu.ec' });
    const f = TestBed.createComponent(StudentContentComponent);
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('Este espacio es para estudiantes');
    http.expectNone('/api/v1/learning/courses');
  });
  it('autoselecciona la única asignatura disponible y limpia un acceso retirado', () => {
    const c = setup().componentInstance;
    expect(c.accessId).toBe('access');
    c.loadCourses();
    http.expectOne('/api/v1/learning/courses').flush([
      { id: 'access-1', course: 'cálculo', teacher: 'Prof. A' },
      { id: 'access-2', course: 'álgebra', teacher: 'Prof. B' },
    ]);
    expect(c.accessId).toBe('');
  });
  it('avanza por los 3 pasos del flujo, prioriza el contenido generado y permite nueva solicitud', () => {
    const f = setup();
    const c = f.componentInstance;
    f.detectChanges();
    expect(c.activeView()).toBe('form');
    expect(c.currentStep()).toBe(1);

    c.topic = 'Espacio muestral';
    c.objective = 'Entender los conceptos';
    c.prepare();
    http.expectOne('/api/v1/learning/prepare').flush({
      id: 'prep-1',
      status: 'prepared',
      topic: 'Espacio muestral',
      learning_objective: 'Entender los conceptos',
      resource_type: 'EXPLANATION',
      difficulty: 'advanced',
      question_count: null,
      sources: [
        {
          id: 'chunk-1',
          document_id: 'doc-1',
          document_title: 'DIAPOSITIVAS 1 PyE',
          filename: 'pye.pdf',
          document_sha256: 'abc',
          source_sha256: 'def',
          processing_version: 'text-v2',
          position: 0,
          source_kind: 'page',
          source_index: 2,
          char_start: 0,
          char_end: 50,
          text: 'Conjunto de todos los resultados posibles.',
          similarity: 0.91,
          citation_id: 'S1',
        },
      ],
    });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0, offset: 0, limit: 10 });
    f.detectChanges();

    expect(c.activeView()).toBe('detail');
    expect(c.currentStep()).toBe(2);
    expect(f.nativeElement.querySelector('#student-sources')?.textContent).toContain('Espacio muestral');

    c.generate();
    http.expectOne('/api/v1/learning/prep-1/generate').flush({
      id: 'prep-1',
      status: 'succeeded',
      message: 'Tu contenido está listo y guardado en el historial.',
      resource: {
        resource_type: 'EXPLANATION',
        title: 'Conceptos fundamentales: El espacio muestral',
        summary: { text: 'El espacio muestral contiene todos los resultados.', citations: ['S1'] },
        steps: [{ text: 'Identificar el experimento.', citations: ['S1'] }],
        worked_example: { text: 'Lanzamiento de un dado: S = {1,2,3,4,5,6}.', citations: ['S1'] },
      },
    });
    http.expectOne('/api/v1/learning/quota').flush({ enabled: true, daily_limit: 5, remaining: 2 });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0, offset: 0, limit: 10 });
    f.detectChanges();

    expect(c.currentStep()).toBe(3);
    expect(f.nativeElement.textContent).toContain('Conceptos fundamentales: El espacio muestral');
    const drawer = f.nativeElement.querySelector('details.sources-drawer') as HTMLDetailsElement | null;
    expect(drawer).not.toBeNull();
    expect(drawer!.open).toBe(false);

    c.startNewRequest();
    f.detectChanges();
    expect(c.activeView()).toBe('form');
    expect(c.currentStep()).toBe(1);
    expect(c.topic).toBe('');
  });
  it('abre una solicitud del historial en vista detalle y permite editarla para buscar otra vez', () => {
    const f = setup();
    const c = f.componentInstance;
    c.open('hist-1');
    http.expectOne('/api/v1/learning/history/hist-1').flush({
      preparation: {
        id: 'hist-1',
        status: 'prepared',
        topic: 'Probabilidad condicional',
        learning_objective: 'Resolver ejemplos prácticos',
        resource_type: 'EXAMPLE',
        difficulty: 'intermediate',
        question_count: null,
        sources: [],
      },
      status: 'prepared',
      created_at: '2026-11-21T11:56:00Z',
      completed_at: null,
      resource: null,
      message: null,
    });
    f.detectChanges();

    expect(c.activeView()).toBe('detail');
    expect(c.openedStatus()).toBe('prepared');
    expect(f.nativeElement.textContent).toContain('Listo para generar');

    c.editCurrentRequest();
    f.detectChanges();
    expect(c.activeView()).toBe('form');
    expect(c.topic).toBe('Probabilidad condicional');
    expect(c.objective).toBe('Resolver ejemplos prácticos');
    expect(c.kind).toBe('EXAMPLE');
    expect(c.difficulty).toBe('intermediate');
  });
  it('renderiza la plantilla sin errores con cuotas y preparaciones mínimas', () => {
    const f = setup();
    const c = f.componentInstance;
    f.detectChanges();
    c.accessId = 'access';
    c.topic = 'Derivadas';
    c.objective = 'Entender la regla';
    c.prepare();
    http.expectOne('/api/v1/learning/prepare').flush({ id: 'preparation', sources: [] });
    http.expectOne('/api/v1/learning/history?offset=0').flush({ items: [], total: 0 });
    f.detectChanges();

    expect(f.nativeElement.querySelector('#student-sources')).not.toBeNull();
    expect(f.nativeElement.textContent).toContain('No se encontraron fragmentos para esta solicitud.');
  });
});
