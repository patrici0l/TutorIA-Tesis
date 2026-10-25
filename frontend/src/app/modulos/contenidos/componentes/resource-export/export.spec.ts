import { TestBed } from '@angular/core/testing';
import { ResourceExportComponent } from './export';
import { ResourceExportService } from '../../servicios/resource-export.service';
import { HistoryDetail } from '../../modelos/history.model';

describe('Exportación desde el historial', () => {
  const detail: HistoryDetail = {
    preparation: {
      id: 'c3ab007f-b3ba-472e-a805-39312ec0a29e',
      status: 'prepared',
      topic: 'Derivadas',
      learning_objective: 'Explicar',
      resource_type: 'EXPLANATION',
      difficulty: 'basic',
      question_count: null,
      sources: [],
    },
    status: 'failed',
    created_at: '2026-10-10T00:00:00Z',
    completed_at: null,
    resource: null,
    message: null,
    audit: null,
  };
  const download = vi.fn();
  beforeEach(() => {
    download.mockReset();
    TestBed.configureTestingModule({
      imports: [ResourceExportComponent],
      providers: [{ provide: ResourceExportService, useValue: { download } }],
    });
  });

  it('descarga también un fallo sin auditoría y anuncia la solicitud', () => {
    const fixture = TestBed.createComponent(ResourceExportComponent);
    fixture.componentRef.setInput('detail', detail);
    fixture.detectChanges();
    fixture.nativeElement.querySelector('button').click();
    fixture.detectChanges();
    expect(download).toHaveBeenCalledExactlyOnceWith(detail);
    expect(fixture.nativeElement.querySelector('[role=status]').textContent).toContain(
      'Se solicitó',
    );
  });

  it('muestra error recuperable sin declarar descarga completada', () => {
    download.mockImplementationOnce(() => {
      throw new Error('Not available');
    });
    const fixture = TestBed.createComponent(ResourceExportComponent);
    fixture.componentRef.setInput('detail', detail);
    fixture.detectChanges();
    fixture.componentInstance.download();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role=alert]').textContent).toContain('No se pudo');
    fixture.componentInstance.download();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role=alert]')).toBeNull();
    expect(fixture.nativeElement.querySelector('[role=status]')).not.toBeNull();
  });

  it('limpia el aviso al cambiar el recurso consultado', () => {
    const fixture = TestBed.createComponent(ResourceExportComponent);
    fixture.componentRef.setInput('detail', detail);
    fixture.detectChanges();
    fixture.componentInstance.download();
    fixture.componentRef.setInput('detail', { ...detail, status: 'prepared' });
    fixture.detectChanges();
    expect(fixture.componentInstance.message()).toBe('');
  });
});
