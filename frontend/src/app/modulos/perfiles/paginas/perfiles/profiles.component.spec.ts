import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { ProfilesComponent } from './profiles.component';

describe('Perfiles sintéticos', () => {
  const user = signal({ rol: 'teacher' });
  function setup() {
    TestBed.configureTestingModule({
      imports: [ProfilesComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user } },
      ],
    });
    const fixture = TestBed.createComponent(ProfilesComponent);
    const component = fixture.componentInstance;
    component.studentId = 'SYN-001';
    component.topic = 'Derivadas';
    component.performance = 42;
    component.attempts = 4;
    component.errorsText = 'regla_potencia';
    return { fixture, component, http: TestBed.inject(HttpTestingController) };
  }
  beforeEach(() => user.set({ rol: 'teacher' }));
  it('exige confirmación y evita doble guardado durante solicitud', () => {
    const { component, http } = setup();
    component.save();
    http.expectNone('/api/v1/profiles');
    component.confirmed = true;
    component.save();
    component.save();
    const call = http.expectOne('/api/v1/profiles');
    expect(call.request.method).toBe('POST');
    expect(call.request.body).toEqual({
      student_id: 'SYN-001',
      topic: 'Derivadas',
      performance: 42,
      attempts: 4,
      frequent_errors: ['regla_potencia'],
      mastery_level: 'low',
      recommended_support: 'reinforcement',
      data_kind: 'synthetic',
    });
    call.flush({
      ...call.request.body,
      id: 'saved',
      created_at: '2026-10-08T02:00:00Z',
      schema_version: 'performance-profile-v1',
    });
    http
      .expectOne('/api/v1/profiles?offset=0&limit=10')
      .flush({ items: [], total: 1, offset: 0, limit: 10 });
    expect(component.selected()?.id).toBe('saved');
    http.verify();
  });
  it('rechaza datos fuera de rango o rol de estudiante sin enviar', () => {
    const { component, http } = setup();
    component.confirmed = true;
    component.performance = 101;
    component.save();
    http.expectNone('/api/v1/profiles');
    component.performance = 42;
    user.set({ rol: 'student' });
    component.save();
    component.load();
    http.expectNone('/api/v1/profiles');
    http.verify();
  });
  it('consulta el detalle como texto, sin inferencia ni HTML activo', async () => {
    const { fixture, component, http } = setup();
    component.open('saved');
    http
      .expectOne('/api/v1/profiles/saved')
      .flush({
        id: 'saved',
        student_id: 'SYN-001',
        topic: '<script>no ejecutar</script>',
        performance: 42,
        attempts: 4,
        frequent_errors: ['regla_potencia'],
        mastery_level: 'low',
        recommended_support: 'reinforcement',
        data_kind: 'synthetic',
        created_at: '2026-10-08T02:00:00Z',
        schema_version: 'performance-profile-v1',
      });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('<script>no ejecutar</script>');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    http.expectNone((req) => req.method === 'POST');
    http.verify();
  });
  it('informa un fallo de guardado sin reintentar', () => {
    const { component, http } = setup();
    component.confirmed = true;
    component.save();
    http.expectOne('/api/v1/profiles').flush({}, { status: 503, statusText: 'Unavailable' });
    expect(component.error()).toContain('Consulta la lista');
    http.expectNone('/api/v1/profiles');
    http.verify();
  });
});
