import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { GenerationQuotaComponent } from './cuota';

describe('Disponibilidad de generación', () => {
  it('muestra el cupo compartido y se recupera de un error sin inventar saldo', async () => {
    await TestBed.configureTestingModule({
      imports: [GenerationQuotaComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    const f = TestBed.createComponent(GenerationQuotaComponent);
    const changes = vi.fn();
    f.componentInstance.statusChange.subscribe(changes);
    const http = TestBed.inject(HttpTestingController);
    f.componentRef.setInput('refresh', 0);
    f.detectChanges();
    expect(changes).toHaveBeenLastCalledWith({ quota: null, loading: true, error: false });
    http.expectOne('/api/v1/content/quota').flush({
      enabled: true,
      used: 2,
      remaining: 3,
      daily_limit: 5,
      resets_at: '2026-10-25T00:00:00Z',
      max_output_tokens: 4096,
      timeout_seconds: 30,
    });
    f.detectChanges();
    expect(changes.mock.lastCall?.[0].quota.enabled).toBe(true);
    expect(f.nativeElement.textContent).toContain('3 de 5 solicitudes disponibles');
    expect(f.nativeElement.textContent).toContain('40% del cupo consumido');
    expect(f.nativeElement.querySelector('svg').getAttribute('aria-label')).toBe('40% del cupo consumido');
    expect(f.nativeElement.querySelector('.ring-used').getAttribute('stroke-dasharray')).toBe('40 100');
    expect(f.componentInstance.usedPercent({ daily_limit: 0, used: 0 } as never)).toBe(0);
    f.componentRef.setInput('refresh', 1);
    f.detectChanges();
    http.expectOne('/api/v1/content/quota').flush({}, { status: 503, statusText: 'Unavailable' });
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('No pudimos consultar');
    expect(changes).toHaveBeenLastCalledWith({ quota: null, loading: false, error: true });
    expect(f.nativeElement.textContent).not.toContain('3 de 5');
    f.nativeElement.querySelector('button').click();
    http.expectOne('/api/v1/content/quota').flush({
      enabled: true,
      used: 5,
      remaining: 0,
      daily_limit: 5,
      resets_at: '2026-10-25T00:00:00Z',
      max_output_tokens: 4096,
      timeout_seconds: 30,
    });
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('Cupo diario agotado');
    http.verify();
  });
});
