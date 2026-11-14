import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { StudentAssignmentsComponent } from './actividades';
import { AssignmentService } from '../../compartido/actividades/actividades.service';
import { AuthService } from '../../inicio/sesion.service';

it('el alumno consulta recursos cerrados sin servicio de generación ni operaciones docentes', async () => {
  const list = vi.fn().mockReturnValue(
    of({
      items: [
        {
          id: 'material',
          title: 'Lectura',
          version: 'resource-v1',
          resource_id: 'resource',
          status: 'closed',
          created_at: '2026-11-07T12:00:00Z',
        },
      ],
      total: 1,
      offset: 0,
      limit: 10,
    }),
  );
  await TestBed.configureTestingModule({
    imports: [StudentAssignmentsComponent],
    providers: [
      provideRouter([]),
      { provide: AssignmentService, useValue: { list } },
      { provide: AuthService, useValue: { user: signal({ rol: 'student' }) } },
    ],
  }).compileComponents();
  const f = TestBed.createComponent(StudentAssignmentsComponent);
  await f.whenStable();
  expect(f.nativeElement.querySelector('form')).toBeNull();
  expect(f.nativeElement.querySelector('a[href="/actividades/material"]').textContent).toContain(
    'Ver recurso',
  );
  expect(list).toHaveBeenCalledWith(0);
});
