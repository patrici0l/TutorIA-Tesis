import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from '../../inicio/sesion.service';
import { ProfilesComponent } from './perfiles';
import { provideRouter } from '@angular/router';

describe('Perfiles sintéticos', () => {
  const user = signal({ rol: 'teacher' });
  function setup() {
    TestBed.configureTestingModule({
      imports: [ProfilesComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
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
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    if (user().rol === 'teacher') {
      http.expectOne('/api/v1/profiles?offset=0&limit=5').flush({ items: [], total: 0, offset: 0, limit: 5 });
    }
    return { fixture, component, http };
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
      .expectOne('/api/v1/profiles?offset=0&limit=5')
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
    http.expectOne('/api/v1/profiles/saved').flush({
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
  it('carga perfiles al entrar y ofrece usar el detalle en Recursos', () => {
    const { fixture, component, http } = setup();
    expect(component.page()?.total).toBe(0);
    component.open('profile-own');
    http.expectOne('/api/v1/profiles/profile-own').flush({
      id: 'profile-own', student_id: 'SYN-001', topic: 'Derivadas', performance: 42,
      attempts: 4, frequent_errors: [], mastery_level: 'low', recommended_support: 'reinforcement',
      data_kind: 'synthetic', created_at: '2026-10-08T00:00:00Z', schema_version: 'performance-profile-v1',
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a.use-profile').getAttribute('href')).toBe('/recursos?profile_id=profile-own');
    http.verify();
  });
  it('explica duplicados junto al campo y conserva los datos para corregirlos', () => {
    const { fixture, component, http } = setup();
    component.confirmed = true;
    component.errorsText = 'regla_potencia\nregla_potencia';
    component.save();
    fixture.detectChanges();
    const field = fixture.nativeElement.querySelector('#frequentErrors');
    expect(field.getAttribute('aria-invalid')).toBe('true');
    expect(field.getAttribute('aria-describedby')).toContain('frequentErrors-error');
    expect(fixture.nativeElement.querySelector('#frequentErrors-error').textContent).toContain('etiquetas repetidas');
    expect(component.errorsText).toBe('regla_potencia\nregla_potencia');
    http.expectNone('/api/v1/profiles');
    component.errorsText = 'regla_potencia';
    component.validateAfterEdit();
    fixture.detectChanges();
    expect(field.getAttribute('aria-invalid')).toBeNull();
    component.save();
    const call = http.expectOne('/api/v1/profiles');
    expect(call.request.body.frequent_errors).toEqual(['regla_potencia']);
    call.flush({}, { status: 503, statusText: 'Unavailable' });
    http.verify();
  });
  it('permite pedir validación sin dejar Guardar bloqueado sin explicación', () => {
    const { fixture, component, http } = setup();
    component.performance = null;
    component.attempts = 0;
    component.confirmed = false;
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('button[type=submit]').disabled).toBe(false);
    component.save();
    fixture.detectChanges();
    expect(component.fieldError('performance')).toContain('entre 0 y 100');
    expect(component.fieldError('attempts')).toContain('número entero');
    expect(component.fieldError('profile-confirmed')).toContain('datos ficticios');
    http.expectNone('/api/v1/profiles');
    http.verify();
  });
});
