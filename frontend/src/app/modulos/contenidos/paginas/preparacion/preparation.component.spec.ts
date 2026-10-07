import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { PreparationComponent } from './preparation.component';

describe('Preparación docente', () => {
  const user = signal({ rol: 'teacher' });
  let http: HttpTestingController;
  const response = {
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
      },
    ],
  };
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
  function setup() {
    const fixture = TestBed.createComponent(PreparationComponent);
    fixture.componentInstance.topic = 'Derivadas';
    fixture.componentInstance.objective = 'Practicar';
    return fixture;
  }
  it('envía contrato mínimo, evita doble envío y muestra fuentes como texto', async () => {
    const fixture = setup(),
      component = fixture.componentInstance;
    fixture.detectChanges();
    component.prepare();
    component.prepare();
    const call = http.expectOne('/api/v1/content/prepare');
    expect(call.request.body).toEqual({
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
});
