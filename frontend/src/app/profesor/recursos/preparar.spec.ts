import { ViewAttention } from '../../compartido/atencion-vista.service';
import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { AuthService } from '../../inicio/sesion.service';
import { PreparationComponent } from './preparar';
import { PreparationResponse } from '../../compartido/recursos/recursos.model';
import { ResourceExportService } from './exportar.service';

describe('Preparación docente', () => {
  const quota = {
    enabled: true,
    daily_limit: 5,
    used: 1,
    remaining: 4,
    resets_at: '2026-10-25T00:00:00Z',
    max_output_tokens: 4096,
    timeout_seconds: 30,
  };
  const user = signal({ rol: 'teacher' });
  let http: HttpTestingController;
  const response: PreparationResponse = {
    id: 'test-prepared',
    status: 'prepared',
    topic: 'Derivadas',
    learning_objective: 'Practicar',
    resource_type: 'EXPLANATION',
    difficulty: 'basic',
    question_count: null,
    sources: [
      {
        id: 'c1',
        citation_id: 'S1',
        document_id: 'd1',
        document_title: 'Fuente sintética',
        filename: 'fuente.txt',
        source_kind: 'paragraph',
        source_index: 1,
        position: 0,
        char_start: 0,
        char_end: 18,
        source_sha256: 'source-hash',
        document_sha256: 'file-hash',
        text: '<script>no ejecutar</script>',
        processing_version: 'test-v1',
        similarity: 0.9,
      },
    ],
  };
  it('envía una preparación una sola vez y muestra un fallo sin reintentar', async () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    component.prepare();
    http.expectOne('/api/v1/content/prepare').flush(response);
    component.generate();
    component.generate();
    const call = http.expectOne('/api/v1/content/test-prepared/generate');
    expect(call.request.body).toEqual({});
    call.flush({
      id: 'test-prepared',
      status: 'failed',
      resource: null,
      message: 'Cuota agotada.',
    });
    fixture.detectChanges();
    http.expectOne('/api/v1/content/quota').flush(quota);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Cuota agotada.');
    component.generate();
    http.expectNone('/api/v1/content/test-prepared/generate');
    component.clearResult();
    expect(component.generation()).toBeNull();
  });
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    await TestBed.configureTestingModule({
      imports: [PreparationComponent],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user } },
      ],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  it('permite reintentar tras un rechazo de cupo sin marcar la preparación como enviada', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    component.prepare();
    http.expectOne('/api/v1/content/prepare').flush(response);
    component.generate();
    http
      .expectOne('/api/v1/content/test-prepared/generate')
      .flush(
        { detail: 'Espera un minuto antes de generar otro recurso.' },
        { status: 429, statusText: 'Too Many Requests' },
      );
    expect(component.sent()).toBe(false);
    fixture.detectChanges();
    http.expectOne('/api/v1/content/quota').flush(quota);
    component.generate();
    http
      .expectOne('/api/v1/content/test-prepared/generate')
      .flush(
        { detail: 'Espera un minuto antes de generar otro recurso.' },
        { status: 429, statusText: 'Too Many Requests' },
      );
  });
  it('ofrece descarga solo al abrir historial y no hace solicitudes al descargar', () => {
    const exportFile = vi
      .spyOn(TestBed.inject(ResourceExportService), 'download')
      .mockImplementation(() => {});
    const fixture = setup();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-resource-export')).toBeNull();
    const detail = {
      preparation: response,
      status: 'failed' as const,
      created_at: '2026-10-10T00:00:00Z',
      completed_at: '2026-10-10T00:01:00Z',
      resource: null,
      message: 'Fallo conservado',
      audit: null,
    };
    fixture.componentInstance.restore(detail);
    fixture.detectChanges();
    fixture.nativeElement.querySelector('app-resource-export button').click();
    expect(exportFile).toHaveBeenCalledExactlyOnceWith(detail);
    http.expectNone(() => true);
    fixture.componentInstance.clearResult();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('app-resource-export')).toBeNull();
    exportFile.mockRestore();
  });
  function setup() {
    const fixture = TestBed.createComponent(PreparationComponent);
    fixture.componentInstance.course = 'Cálculo Diferencial';
    fixture.componentInstance.topic = 'Derivadas';
    fixture.componentInstance.objective = 'Practicar';
    fixture.detectChanges();
    http.expectOne('/api/v1/content/quota').flush(quota);
    http.expectOne('/api/v1/documents?limit=5&offset=0').flush({
      items: [
        {
          course: 'Cálculo Diferencial',
          status: 'uploaded',
          published_at: '2026-11-12T23:00:00Z',
          permission_recorded_at: '2026-11-12T22:00:00Z',
          processing_status: 'processed',
          index_status: 'indexed',
        },
      ],
      total: 1,
      limit: 5,
      offset: 0,
    });
    return fixture;
  }
  it('recupera un recurso guardado y bloquea su reenvío sin POST', () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    component.restore({
      preparation: response,
      status: 'succeeded',
      created_at: '2026-10-07T22:00:00Z',
      completed_at: '2026-10-07T22:00:01Z',
      resource: null,
      message: null,
    });
    expect(component.result()?.id).toBe('test-prepared');
    expect(component.sent()).toBe(true);
    expect(component.generation()?.status).toBe('succeeded');
    component.generate();
    http.expectNone((req) => req.method === 'POST');
    component.restore({
      preparation: response,
      status: 'generating',
      created_at: '2026-10-07T22:00:00Z',
      completed_at: null,
      resource: null,
      message: null,
    });
    expect(component.restoredPending()).toBe(true);
    component.generate();
    http.expectNone((req) => req.method === 'POST');
    component.restore({
      preparation: response,
      status: 'prepared',
      created_at: '2026-10-07T22:00:00Z',
      completed_at: null,
      resource: null,
      message: null,
    });
    expect(component.sent()).toBe(false);
  });
  it('envía contrato mínimo, evita doble envío y muestra fuentes como texto', async () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    fixture.detectChanges();
    component.prepare();
    component.prepare();
    const call = http.expectOne('/api/v1/content/prepare');
    expect(call.request.body).toEqual({
      course: 'Cálculo Diferencial',
      topic: 'Derivadas',
      learning_objective: 'Practicar',
      resource_type: 'EXPLANATION',
      difficulty: 'basic',
    });
    call.flush(response);
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('PREPARADO, SIN GENERAR');
    expect(fixture.nativeElement.querySelector('blockquote').textContent).toBe(
      response.sources[0].text,
    );
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    component.clearResult();
    expect(component.result()).toBeNull();
  });
  it('solo envía campos del recurso seleccionado y elimina respuesta al cambiar', () => {
    const component = setup().componentInstance;
    component.resourceType = 'FEEDBACK';
    component.studentAnswer = 'Respuesta de prueba';
    component.prepare();
    const feedback = http.expectOne('/api/v1/content/prepare');
    expect(feedback.request.body.student_answer).toBe('Respuesta de prueba');
    expect(feedback.request.body.question_count).toBeUndefined();
    feedback.flush(response);
    component.resourceType = 'QUIZ';
    component.changeResource();
    expect(component.studentAnswer).toBe('');
    component.prepare();
    const quiz = http.expectOne('/api/v1/content/prepare');
    expect(quiz.request.body.question_count).toBe(3);
    expect(quiz.request.body.student_answer).toBeUndefined();
    quiz.flush(response);
  });
  it('maneja falta de fuentes y permite volver a enviar sin reintentos automáticos', () => {
    const component = setup().componentInstance;
    component.prepare();
    http
      .expectOne('/api/v1/content/prepare')
      .flush({ detail: 'No hay fuentes disponibles.' }, { status: 422, statusText: 'No sources' });
    expect(component.loading()).toBe(false);
    expect(component.error()).toBe('No hay fuentes disponibles.');
    expect(component.result()).toBeNull();
    component.prepare();
    http.expectOne('/api/v1/content/prepare').flush(response);
    expect(component.result()?.id).toBe('test-prepared');
  });
  it('selecciona un perfil propio y envía únicamente su identificador', async () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    component.loadProfiles();
    const profile = {
      id: 'profile-test',
      student_id: 'SYN-001',
      topic: 'Derivadas',
      performance: 42,
      mastery_level: 'low' as const,
      created_at: '2026-10-08T00:00:00Z',
    };
    http
      .expectOne('/api/v1/profiles?offset=0&limit=10')
      .flush({ items: [profile], total: 1, offset: 0, limit: 10 });
    component.chooseProfile(profile);
    component.objective = 'Practicar';
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#difficulty').disabled).toBe(true);
    component.prepare();
    const call = http.expectOne('/api/v1/content/prepare');
    expect(call.request.body.profile_id).toBe('profile-test');
    expect(call.request.body.profile).toBeUndefined();
    call.flush(response);
    component.chooseProfile(null);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#difficulty').disabled).toBe(false);
    expect(component.result()).toBeNull();
  });
  it('muestra la adaptación conservada sin generar al abrir historial', () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    const adaptation = {
      policy_version: 'profile-adaptation-v1',
      profile: {
        id: 'p1',
        student_id: 'SYN-001',
        topic: 'Derivadas',
        performance: 42,
        attempts: 4,
        mastery_level: 'low' as const,
        recommended_support: 'reinforcement' as const,
        frequent_errors: ['<script>no ejecutar</script>'],
        data_kind: 'synthetic' as const,
        schema_version: 'performance-profile-v1' as const,
        created_at: '2026-10-08T00:00:00Z',
      },
      requested_difficulty: 'advanced' as const,
      effective_difficulty: 'basic' as const,
      guidance: 'Paso a paso',
      reason: 'Dominio bajo informado',
      focus_errors: ['<script>no ejecutar</script>'],
      suggested_resources: ['EXERCISE' as const],
    };
    component.restore({
      preparation: { ...response, adaptation },
      status: 'prepared',
      created_at: '2026-10-08T00:00:00Z',
      completed_at: null,
      resource: null,
      message: null,
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Dominio bajo informado');
    expect(fixture.nativeElement.textContent).toContain('Aplicada: Básica');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    http.expectNone('/api/v1/content/prepare');
    http.expectNone('/api/v1/content/test-prepared/generate');
  });
  it('rechaza campos incompletos y evita peticiones del estudiante', () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    component.resourceType = 'FEEDBACK';
    component.prepare();
    expect(component.error()).toBeTruthy();
    user.set({ rol: 'student' });
    component.studentAnswer = 'Prueba';
    component.prepare();
    fixture.detectChanges();
    http.expectNone('/api/v1/content/prepare');
    expect(fixture.nativeElement.textContent).toContain('Espacio docente');
  });
  it('presenta las fuentes antes de generar y retira esa acción al recuperar un recurso finalizado', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    component.restore({
      preparation: response,
      status: 'prepared',
      created_at: '2026-10-24T12:00:00Z',
      completed_at: null,
      resource: null,
      message: null,
    });
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    const sources = root.querySelector<HTMLDetailsElement>('.source-review')!;
    const generate = Array.from(root.querySelectorAll('button')).find((button) =>
      button.textContent?.includes('Generar recurso con estas fuentes'),
    )!;
    expect(sources.open).toBe(true);
    expect(
      sources.compareDocumentPosition(generate) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    component.restore({
      preparation: response,
      status: 'succeeded',
      created_at: '2026-10-24T12:00:00Z',
      completed_at: '2026-10-24T12:00:01Z',
      resource: {
        resource_type: 'EXPLANATION',
        title: 'Recurso',
        summary: { text: 'Concepto', citations: ['S1'] },
        steps: [],
        worked_example: { text: 'Ejemplo', citations: ['S1'] },
      },
      message: null,
    });
    fixture.detectChanges();
    expect(
      Array.from(root.querySelectorAll('button')).some((button) =>
        button.textContent?.includes('Generar recurso con estas fuentes'),
      ),
    ).toBe(false);
    expect(root.querySelector('a[href^="/actividades"]')?.getAttribute('href')).toContain(
      'resource=test-prepared',
    );
    http.expectNone('/api/v1/content/test-prepared/generate');
  });
  it('pide la asignatura antes de preparar un recurso', () => {
    const component = setup().componentInstance;
    component.course = '  ';
    component.prepare();
    http.expectNone('/api/v1/content/prepare');
    expect(component.loading()).toBe(false);
    expect(component.error()).toBeTruthy();
  });
  it('lleva las fuentes a primer plano y permite volver al formulario sin reenviar', () => {
    const fixture = setup();
    const attention = vi.spyOn(TestBed.inject(ViewAttention), 'reveal');
    const component = fixture.componentInstance;
    component.prepare();
    http.expectOne('/api/v1/content/prepare').flush(response);
    fixture.detectChanges();
    expect(component.editing()).toBe(false);
    expect(attention).toHaveBeenLastCalledWith('sources-title');
    expect(fixture.nativeElement.querySelector('.workspace').hidden).toBe(true);
    expect(fixture.nativeElement.querySelector('#sources-title')).toBeTruthy();
    component.showEditor();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.workspace').hidden).toBe(false);
    expect(component.topic).toBe('Derivadas');
    expect(attention).toHaveBeenLastCalledWith('prepare-title');
    http.expectNone((req) => req.method === 'POST');
  });
  it('abre un recurso del historial en su vista y muestra los errores en el destino visible', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    const attention = vi.spyOn(TestBed.inject(ViewAttention), 'reveal');
    component.showSaved();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=5')
      .flush({ items: [], total: 0, offset: 0, limit: 10 });
    expect(component.workspaceMode()).toBe('saved');
    component.restore({
      preparation: response,
      status: 'prepared',
      created_at: '',
      completed_at: null,
      resource: null,
      message: null,
    });
    fixture.detectChanges();
    expect(component.workspaceMode()).toBe('create');
    expect(component.editing()).toBe(false);
    expect(attention).toHaveBeenLastCalledWith('sources-title');
    component.generate();
    http
      .expectOne('/api/v1/content/test-prepared/generate')
      .flush({ detail: 'Cupo agotado' }, { status: 429, statusText: 'Too Many Requests' });
    fixture.detectChanges();
    http.expectOne('/api/v1/content/quota').flush(quota);
    expect(attention).toHaveBeenLastCalledWith('resource-error');
    expect(fixture.nativeElement.querySelector('#resource-error').textContent).toContain(
      'Cupo agotado',
    );
  });
  it('muestra primero asignaturas y continúa solo con material habilitado', () => {
    const fixture = setup();
    const component = fixture.componentInstance;
    fixture.detectChanges();
    const root: HTMLElement = fixture.nativeElement;
    expect(root.querySelector('#resource-course')!.getAttribute('role')).toBe('combobox');
    expect(root.querySelector('.profile-options')).toBeNull();
    expect(component.inputStep()).toBe('course');
    component.continueWithCourse();
    fixture.detectChanges();
    expect(component.inputStep()).toBe('details');
    component.showCourse();
    component.courses.set([
      { value: 'Probabilidad', label: 'Probabilidad', documents: 2, enabled: 0 },
    ]);
    component.course = 'Probabilidad';
    component.chooseCourse();
    component.continueWithCourse();
    fixture.detectChanges();
    expect(component.inputStep()).toBe('course');
    expect(root.textContent).toContain('aún no hay material habilitado');
    expect(root.querySelector('a[href^="/documentos"]')!.getAttribute('href')).toContain(
      'course=Probabilidad',
    );
    http.expectNone((req) => req.method === 'POST');
  });
  it('no inventa materias cuando el catálogo está vacío y permite recuperar errores', () => {
    const fixture = TestBed.createComponent(PreparationComponent);
    fixture.detectChanges();
    http.expectOne('/api/v1/content/quota').flush(quota);
    http
      .expectOne('/api/v1/documents?limit=5&offset=0')
      .flush({ detail: 'Error' }, { status: 500, statusText: 'Error' });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se pudieron consultar tus asignaturas');
    fixture.componentInstance.loadCourses();
    http
      .expectOne('/api/v1/documents?limit=5&offset=0')
      .flush({ items: [], total: 0, limit: 5, offset: 0 });
    fixture.detectChanges();
    expect(fixture.componentInstance.courses()).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Subir mi primer documento');
  });
  it('abre directamente el selector de recursos al llegar desde asignaciones', async () => {
    const snapshot = TestBed.inject(ActivatedRoute).snapshot;
    vi.spyOn(snapshot, 'queryParamMap', 'get').mockReturnValue(
      convertToParamMap({ view: 'saved', action: 'assign' }),
    );
    const fixture = setup();
    await fixture.whenStable();
    http
      .expectOne('/api/v1/content/history?offset=0&limit=5')
      .flush({ items: [], total: 0, offset: 0, limit: 10 });
    fixture.detectChanges();
    expect(fixture.componentInstance.workspaceMode()).toBe('saved');
    expect(fixture.nativeElement.querySelector('#history-title').textContent).toContain(
      'Elige un recurso para asignar',
    );
    http.expectNone((request) => request.method === 'POST');
  });
});
