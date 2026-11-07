import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { GenerationQuotaComponent } from './quota';

describe('Disponibilidad de generación', () => {
  it('muestra el cupo compartido y se recupera de un error sin inventar saldo', async () => {
    await TestBed.configureTestingModule({
      imports: [GenerationQuotaComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    const f = TestBed.createComponent(GenerationQuotaComponent);
    const http = TestBed.inject(HttpTestingController);
    f.componentRef.setInput('refresh', 0);
    f.detectChanges();
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
    expect(f.nativeElement.textContent).toContain('3 de 5 solicitudes disponibles');
    expect(f.nativeElement.textContent).toContain('40% del cupo consumido');
    f.componentRef.setInput('refresh', 1);
    f.detectChanges();
    http.expectOne('/api/v1/content/quota').flush({}, { status: 503, statusText: 'Unavailable' });
    f.detectChanges();
    expect(f.nativeElement.textContent).toContain('No pudimos consultar');
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
