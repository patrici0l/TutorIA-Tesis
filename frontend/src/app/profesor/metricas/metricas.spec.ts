import { NgxEchartsDirective } from 'ngx-echarts';
import { Directive, input, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from '../../inicio/sesion.service';
import { MetricsComponent } from './metricas';

@Directive({ selector: '[echarts]' })
class ChartStub {
  readonly options = input<unknown>();
}

describe('Métricas privadas', () => {
  const user = signal({ rol: 'teacher' });
  function setup() {
    TestBed.configureTestingModule({
      imports: [MetricsComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: AuthService, useValue: { user } },
      ],
    });
    TestBed.overrideComponent(MetricsComponent, {
      remove: { imports: [NgxEchartsDirective] },
      add: { imports: [ChartStub] },
    });
    return {
      fixture: TestBed.createComponent(MetricsComponent),
      http: TestBed.inject(HttpTestingController),
    };
  }
  beforeEach(() => user.set({ rol: 'teacher' }));
  it('muestra ausencias como sin datos, con cobertura, y consulta solo una vez', async () => {
    const { fixture, http } = setup();
    fixture.componentInstance.load();
    const tokens = { known_sum: null, known_records: 0, unknown_records: 1 };
    const call = http.expectOne('/api/v1/metrics');
    expect(call.request.method).toBe('GET');
    call.flush({
      daily: [
        {
          day: '2026-10-08',
          records: 1,
          input_tokens: 0,
          output_tokens: null,
          latency_ms: '1500',
          latency_records: 1,
        },
      ],
      scope: 'own_all_time',
      observed_at: '2026-10-08T23:00:00Z',
      total_records: 2,
      prepared: 1,
      generating: 0,
      succeeded: 0,
      failed: 1,
      reserved_attempts: 1,
      execution_records: 1,
      input_tokens: tokens,
      output_tokens: tokens,
      total_tokens: tokens,
      latency: {
        known_average_ms: null,
        known_min_ms: null,
        known_max_ms: null,
        known_records: 0,
        unknown_records: 1,
      },
      cost_known_records: 0,
      cost_unknown_records: 1,
    });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Sin datos');
    expect(fixture.nativeElement.textContent).toContain('1 sin dato');
    expect(fixture.nativeElement.textContent).toContain('no verifica facturación');
    const charts = fixture.componentInstance.charts()!;
    expect(charts.hasTokens).toBe(true);
    expect(charts.hasLatency).toBe(true);
    const tokenSeries = charts.tokens['series'] as { data: (number | null)[] }[];
    const latencySeries = charts.latency['series'] as { data: (number | null)[] }[];
    expect(tokenSeries[0].data).toHaveLength(30);
    expect(tokenSeries[0].data[29]).toBe(0);
    expect(tokenSeries[0].data[28]).toBeNull();
    expect(tokenSeries[1].data[29]).toBeNull();
    expect(latencySeries[0].data[29]).toBe(1.5);
    expect(fixture.nativeElement.querySelector('.states')).toBeNull();
    http.expectNone((req) => req.method === 'POST');
    http.verify();
  });
  it('permite reintentar la lectura tras fallo sin reintento automático', () => {
    const { fixture, http } = setup();
    http.expectOne('/api/v1/metrics').flush({}, { status: 503, statusText: 'Unavailable' });
    expect(fixture.componentInstance.error()).toContain('No se pudieron');
    expect(fixture.componentInstance.busy()).toBe(false);
    http.expectNone('/api/v1/metrics');
    fixture.componentInstance.load();
    http.expectOne('/api/v1/metrics').flush({}, { status: 503, statusText: 'Unavailable' });
    http.verify();
  });
  it('no consulta con rol de estudiante', async () => {
    user.set({ rol: 'student' });
    const { fixture, http } = setup();
    fixture.componentInstance.load();
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('requiere permisos de docente');
    http.expectNone('/api/v1/metrics');
    http.verify();
  });
});
