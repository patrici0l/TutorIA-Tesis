import { NgxEchartsDirective, provideEchartsCore } from 'ngx-echarts';
import * as echarts from 'echarts/core';
import { BarChart, LineChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  AriaComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { EChartsCoreOption } from 'echarts/core';
echarts.use([
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  AriaComponent,
  CanvasRenderer,
]);
// Presenta uso de generación y distingue valores conocidos de datos no registrados.
import { Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../inicio/sesion.service';
import { MetricsSummary } from './metricas.model';
import { MetricsService } from './metricas.service';

@Component({
  selector: 'app-generation-metrics',
  providers: [provideEchartsCore({ echarts })],
  imports: [NgxEchartsDirective, DatePipe, RouterLink],
  templateUrl: './metricas.html',
  styleUrl: './metricas.scss',
})
export class MetricsComponent {
  private readonly auth = inject(AuthService);
  private readonly service = inject(MetricsService);
  private readonly destroy = inject(DestroyRef);
  readonly allowed = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly busy = signal(false);
  readonly error = signal('');
  readonly summary = signal<MetricsSummary | null>(null);
  readonly charts = computed(() => {
    const d = this.summary();
    if (!d) return null;
    const byDay = new Map((d.daily ?? []).map((point) => [point.day, point]));
    const end = new Date(new Date(d.observed_at).getTime() - 5 * 3600000);
    const days = Array.from({ length: 30 }, (_, index) => {
      const date = new Date(end);
      date.setUTCDate(date.getUTCDate() - 29 + index);
      const day = date.toISOString().slice(0, 10);
      return (
        byDay.get(day) ?? {
          day,
          records: 0,
          input_tokens: null,
          output_tokens: null,
          latency_ms: null,
          latency_records: 0,
        }
      );
    });
    const base = {
      color: ['#2563a6', '#23a28a', '#bd8540', '#a85b65'],
      aria: { enabled: true },
      textStyle: { fontFamily: 'sans-serif', fontSize: 11 },
      tooltip: { trigger: 'axis', confine: true },
      grid: { left: 55, right: 24, top: 30, bottom: 35 },
      animationDuration: 300,
    };
    const timeline = {
      ...base,
      legend: { top: 0, itemWidth: 12, textStyle: { fontSize: 11 } },
      grid: { left: 55, right: 24, top: 38, bottom: 35 },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: days.map((p) => p.day.slice(5).split('-').reverse().join('/')),
      },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#e9edf2' } } },
    };
    return {
      hasTokens: days.some((p) => p.input_tokens !== null || p.output_tokens !== null),
      hasLatency: days.some((p) => p.latency_ms !== null),
      states: {
        ...base,
        grid: { left: 85, right: 35, top: 10, bottom: 25 },
        xAxis: { type: 'value', minInterval: 1 },
        yAxis: { type: 'category', data: ['Con fallo', 'En proceso', 'Por enviar', 'Generadas'] },
        series: [
          {
            type: 'bar',
            barMaxWidth: 18,
            label: { show: true, position: 'right' },
            data: [
              { value: d.failed, itemStyle: { color: '#a85b65' } },
              { value: d.generating, itemStyle: { color: '#bd8540' } },
              { value: d.prepared, itemStyle: { color: '#2563a6' } },
              { value: d.succeeded, itemStyle: { color: '#23a28a' } },
            ],
          },
        ],
      } as EChartsCoreOption,
      totals: {
        ...base,
        xAxis: { type: 'category', data: ['Entrada', 'Salida', 'Total reportado'] },
        yAxis: { type: 'value', name: 'Tokens' },
        series: [
          {
            name: 'Tokens acumulados',
            type: 'bar',
            barMaxWidth: 28,
            label: { show: true, position: 'top' },
            data: [d.input_tokens.known_sum, d.output_tokens.known_sum, d.total_tokens.known_sum],
          },
        ],
      } as EChartsCoreOption,
      tokens: {
        ...timeline,
        series: [
          {
            name: 'Entrada',
            type: 'line',
            smooth: false,
            connectNulls: false,
            symbolSize: 5,
            data: days.map((p) => p.input_tokens),
          },
          {
            name: 'Salida',
            type: 'line',
            smooth: false,
            connectNulls: false,
            symbolSize: 5,
            data: days.map((p) => p.output_tokens),
          },
        ],
      } as EChartsCoreOption,
      latency: {
        ...timeline,
        yAxis: { type: 'value', name: 'Segundos' },
        series: [
          {
            name: 'Respuesta media',
            type: 'line',
            connectNulls: false,
            symbolSize: 5,
            areaStyle: { opacity: 0.06 },
            data: days.map((p) => (p.latency_ms === null ? null : Number(p.latency_ms) / 1000)),
          },
        ],
      } as EChartsCoreOption,
    };
  });
  constructor() {
    this.load();
  }
  load() {
    if (!this.allowed() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.summary.set(null);
    this.service
      .summary()
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (summary) => {
          this.summary.set(summary);
          this.busy.set(false);
        },
        error: () => {
          this.error.set('No se pudieron consultar tus métricas. Puedes volver a intentarlo.');
          this.busy.set(false);
        },
      });
  }
}
