import { PreparationService } from '../../contenidos/servicios/preparation.service';
import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { of, Subject, throwError } from 'rxjs';
import { AuthService } from '../../../nucleo/servicios/auth.service';
import { AssignmentService } from '../../actividades/servicios/assignment.service';
import { Assignment } from '../../actividades/modelos/assignment.model';
import { TeacherAssignmentsComponent } from './assignments';
import { StudentAssignmentsComponent } from '../../estudiante/actividades/assignments';

describe('Actividades asignadas', () => {
  const user = signal({ rol: 'teacher' });
  const detail = vi.fn();
  let resourceParam = '';
  const service = { list: vi.fn(), create: vi.fn(), changeStatus: vi.fn() };
  beforeEach(async () => {
    user.set({ rol: 'teacher' });
    resourceParam = '';
    detail.mockReset();
    service.list.mockReset().mockReturnValue(of({ items: [], total: 0, offset: 0, limit: 10 }));
    service.create.mockReset();
    service.changeStatus.mockReset();
    await TestBed.configureTestingModule({
      imports: [TeacherAssignmentsComponent, StudentAssignmentsComponent],
      providers: [
        provideRouter([]),
        { provide: PreparationService, useValue: { detail } },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              get queryParamMap() {
                return convertToParamMap(resourceParam ? { resource: resourceParam } : {});
              },
            },
          },
        },
        { provide: AuthService, useValue: { user, mode: signal('mock') } },
        { provide: AssignmentService, useValue: service },
      ],
    }).compileComponents();
  });
  it('asigna el recurso seleccionado y conserva el identificador al reintentar', async () => {
    resourceParam = 'integral-id';
    detail.mockReturnValue(
      of({
        status: 'succeeded',
        preparation: { id: resourceParam },
        resource: { title: 'Integrales' },
      }),
    );
    service.create.mockReturnValue(throwError(() => new Error('offline')));
    const f = TestBed.createComponent(TeacherAssignmentsComponent);
    await f.whenStable();
    const c = f.componentInstance;
    c.email = 'estudiante.demo@example.org';
    c.create();
    c.create();
    expect(service.create.mock.calls[0][0]).toMatchObject({
      resource_id: resourceParam,
      version: 'resource-v1',
      title: 'Integrales',
    });
    expect(service.create.mock.calls[0][0].id).toBe(service.create.mock.calls[1][0].id);
    expect(f.nativeElement.textContent).toContain('sin calificación automática');
  });
  it('bloquea un recurso pendiente o inaccesible sin asignar derivadas por error', async () => {
    resourceParam = 'pending-id';
    detail.mockReturnValue(of({ status: 'prepared', resource: null }));
    const f = TestBed.createComponent(TeacherAssignmentsComponent);
    await f.whenStable();
    f.componentInstance.title = 'Integrales';
    f.componentInstance.email = 'estudiante.demo@example.org';
    f.componentInstance.create();
    expect(service.create).not.toHaveBeenCalled();
    expect(f.nativeElement.textContent).toContain('antes de asignarlo');
  });
  it('oculta creación al estudiante y muestra enlace a su actividad', async () => {
    user.set({ rol: 'student' });
    service.list.mockReturnValue(
      of({
        items: [
          {
            id: 'abc',
            status: 'open',
            title: 'Reglas',
            version: 'reglas-v1',
            attempts: 0,
            best_score: null,
            created_at: '2026-10-14T12:00:00Z',
          },
        ],
        total: 1,
        offset: 0,
        limit: 10,
      }),
    );
    const f = TestBed.createComponent(StudentAssignmentsComponent);
    await f.whenStable();
    expect(f.nativeElement.querySelector('form')).toBeNull();
    expect(f.nativeElement.querySelector('a[href="/actividades/abc"]')).not.toBeNull();
    expect(service.create).not.toHaveBeenCalled();
  });
  it('reutiliza identificador al reintentar y evita envíos simultáneos', async () => {
    const f = TestBed.createComponent(TeacherAssignmentsComponent);
    await f.whenStable();
    const c = f.componentInstance;
    c.title = ' Repaso ';
    c.email = 'estudiante.demo@example.org';
    service.create.mockReturnValueOnce(throwError(() => new Error('offline')));
    c.create();
    const id = service.create.mock.calls[0][0].id;
    const pending = new Subject<Assignment>();
    service.create.mockReturnValue(pending);
    c.create();
    c.create();
    expect(service.create).toHaveBeenCalledTimes(2);
    expect(service.create.mock.calls[1][0].id).toBe(id);
    pending.next({} as Assignment);
    pending.complete();
    expect(c.success()).toContain('Actividad asignada');
  });
  it('confirma antes de cerrar, permite reintentar y conserva resultados', async () => {
    const item: Assignment = {
      id: 'abc',
      title: 'Reglas',
      version: 'reglas-v1',
      instructions: '',
      student_email: 'estudiante.demo@example.org',
      created_at: '2026-10-15T12:00:00Z',
      status: 'open',
      status_changed_at: null,
      attempts: 1,
      best_score: 3,
    };
    service.list.mockReturnValue(of({ items: [item], total: 1, offset: 0, limit: 10 }));
    const f = TestBed.createComponent(TeacherAssignmentsComponent);
    await f.whenStable();
    const c = f.componentInstance;
    const button = (label: string) =>
      Array.from(f.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
        (b) => b.textContent?.trim() === label,
      )!;
    button('Cerrar actividad').click();
    await f.whenStable();
    expect(service.changeStatus).not.toHaveBeenCalled();
    expect(f.nativeElement.textContent).toContain('Los resultados guardados se conservan');
    service.changeStatus.mockReturnValueOnce(
      throwError(() => ({
        error: { detail: 'El estado cambió. Actualiza las actividades antes de continuar.' },
      })),
    );
    button('Confirmar cambio').click();
    await f.whenStable();
    expect(f.nativeElement.querySelector('[role=alert]').textContent).toContain('El estado cambió');
    expect(c.page()!.items[0].status).toBe('open');
    const pending = new Subject<Assignment>();
    service.changeStatus.mockReturnValue(pending);
    button('Confirmar cambio').click();
    c.confirmStatus();
    expect(service.changeStatus).toHaveBeenCalledTimes(2);
    pending.next({ ...item, status: 'closed', status_changed_at: '2026-10-15T13:00:00Z' });
    pending.complete();
    await f.whenStable();
    expect(c.page()!.items[0].best_score).toBe(3);
    expect(button('Reactivar actividad')).toBeDefined();
    expect(f.nativeElement.textContent).toContain('Cerrada');
    expect(c.pendingChange()).toBeNull();
    user.set({ rol: 'student' });
    c.requestStatus(c.page()!.items[0], 'open');
    c.confirmStatus();
    await f.whenStable();
    expect(service.changeStatus).toHaveBeenCalledTimes(2);
    service.list.mockReturnValue(of({ items: c.page()!.items, total: 1, offset: 0, limit: 10 }));
    f.destroy();
    const student = TestBed.createComponent(StudentAssignmentsComponent);
    await student.whenStable();
    expect(student.nativeElement.textContent).not.toContain('Reactivar actividad');
    expect(student.nativeElement.querySelector('a[href="/actividades/abc"]').textContent).toContain(
      'Ver actividad y resultados',
    );
  });
  it('al cambiar un recurso por ejercicios muestra y envía solo el contenido elegido', async () => {
    resourceParam = 'integral-id';
    detail.mockReturnValue(
      of({
        status: 'succeeded',
        preparation: { id: resourceParam },
        resource: { title: 'Integrales' },
      }),
    );
    service.create.mockReturnValue(throwError(() => new Error('offline')));
    const f = TestBed.createComponent(TeacherAssignmentsComponent);
    await f.whenStable();
    const c = f.componentInstance;
    const content = f.nativeElement.querySelector('select[name="version"]') as HTMLSelectElement;
    content.value = c.banks[0].version;
    content.dispatchEvent(new Event('change', { bubbles: true }));
    await f.whenStable();
    c.email = 'estudiante.demo@example.org';
    expect(f.nativeElement.textContent).not.toContain('Se comparte con sus fuentes y soluciones');
    c.create();
    expect(service.create.mock.calls[0][0].resource_id).toBeUndefined();
    expect(service.create.mock.calls[0][0].version).toBe(c.banks[0].version);
    expect(f.nativeElement.querySelector('a[href="/practica"]')).toBeNull();
  });
});
