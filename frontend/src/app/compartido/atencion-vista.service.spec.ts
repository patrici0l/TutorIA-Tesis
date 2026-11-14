import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ViewAttention } from './atencion-vista.service';

@Component({
  template:
    '<h2 id="target" tabindex="-1">Resultado</h2><div hidden><h2 id="hidden-target" tabindex="-1">Oculto</h2></div>',
})
class AttentionHost {}

describe('Foco y desplazamiento al resultado', () => {
  afterEach(() => vi.unstubAllGlobals());

  async function setup(reduced = false) {
    vi.stubGlobal(
      'matchMedia',
      vi.fn(() => ({ matches: reduced })),
    );
    await TestBed.configureTestingModule({ imports: [AttentionHost] }).compileComponents();
    const fixture = TestBed.createComponent(AttentionHost);
    fixture.detectChanges();
    const target: HTMLElement = fixture.nativeElement.querySelector('#target');
    const scroll = vi.fn();
    const animate = vi.fn();
    Object.assign(target, { scrollIntoView: scroll, animate });
    return { fixture, target, scroll, animate, attention: TestBed.inject(ViewAttention) };
  }

  it('enfoca y resalta después del render; respeta movimiento reducido', async () => {
    const { fixture, target, scroll, animate, attention } = await setup(true);
    attention.reveal('target');
    fixture.detectChanges();
    await fixture.whenStable();
    expect(document.activeElement).toBe(target);
    expect(scroll).toHaveBeenCalledWith({ behavior: 'instant', block: 'start' });
    expect(animate).not.toHaveBeenCalled();
  });

  it('anima solo el destino vigente y no enfoca contenido oculto', async () => {
    const { fixture, target, scroll, animate, attention } = await setup();
    attention.reveal('target');
    attention.reveal('hidden-target');
    fixture.detectChanges();
    await fixture.whenStable();
    expect(scroll).not.toHaveBeenCalled();
    attention.reveal(target);
    fixture.detectChanges();
    await fixture.whenStable();
    expect(scroll).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' });
    expect(animate).toHaveBeenCalledOnce();
  });
});
