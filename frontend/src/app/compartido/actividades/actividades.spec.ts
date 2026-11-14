import { signal } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../../inicio/sesion.service';
import { AssignmentService } from './actividades.service';
import { AssignmentsComponent } from './actividades';

describe('Actividades: selección de vista por sesión', () => {
  const user = signal({ rol: 'student' });
  const service = { list: vi.fn(), create: vi.fn(), changeStatus: vi.fn() };
  beforeEach(async () => {
    user.set({ rol: 'student' });
    service.list.mockReset().mockReturnValue(
      of({
        items: [
          {
            id: 'assigned',
            title: 'Actividad',
            version: 'reglas-v1',
            status: 'open',
            attempts: 0,
            best_score: null,
            created_at: '2026-11-07T12:00:00Z',
          },
        ],
        total: 1,
        limit: 10,
        offset: 0,
      }),
    );
    service.create.mockReset();
    service.changeStatus.mockReset();
    await TestBed.configureTestingModule({
      imports: [AssignmentsComponent],
      providers: [
        provideRouter([]),
        provideHttpClient(),
        { provide: AuthService, useValue: { user, mode: signal('mock') } },
        { provide: AssignmentService, useValue: service },
      ],
    }).compileComponents();
  });
  it.each(['teacher', 'admin', 'student'])('presenta solo las acciones de %s', async (rol) => {
    user.set({ rol });
    const f = TestBed.createComponent(AssignmentsComponent);
    await f.whenStable();
    expect(!!f.nativeElement.querySelector('form')).toBe(rol !== 'student');
    expect(!!f.nativeElement.querySelector('a[href="/actividades/assigned"]')).toBe(
      rol === 'student',
    );
    expect(service.create).not.toHaveBeenCalled();
    expect(service.changeStatus).not.toHaveBeenCalled();
  });
  it('retira el formulario y las acciones docentes si cambia la sesión a estudiante', async () => {
    user.set({ rol: 'teacher' });
    const f = TestBed.createComponent(AssignmentsComponent);
    await f.whenStable();
    expect(f.nativeElement.querySelector('form')).toBeTruthy();
    user.set({ rol: 'student' });
    await f.whenStable();
    expect(f.nativeElement.querySelector('form')).toBeNull();
    expect(f.nativeElement.textContent).not.toContain('Cerrar actividad');
    expect(f.nativeElement.querySelector('a[href="/actividades/assigned"]')).toBeTruthy();
  });
});
