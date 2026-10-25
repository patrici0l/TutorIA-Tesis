import { Component, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MathTextDirective } from './math-text.directive';

@Component({ imports: [MathTextDirective], template: '<span [appMathText]="text()"></span>' })
class MathHost {
  readonly text = signal('');
}

describe('Texto matemático', () => {
  it('renderiza fracciones e integrales en la primera detección y al cambiar el texto', () => {
    const fixture = TestBed.createComponent(MathHost);
    fixture.componentInstance.text.set(String.raw`Calcula \(\frac{1}{2}\) y $$\int_0^1 x dx$$`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('.katex').length).toBe(2);
    expect(fixture.nativeElement.querySelector('math mfrac')).not.toBeNull();
    fixture.componentInstance.text.set(String.raw`Ahora $\frac{3}{4}$`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('.katex').length).toBe(1);
    expect(fixture.nativeElement.textContent).not.toContain('Calcula');
    fixture.componentInstance.text.set(String.raw`\[\int x dx\]`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.katex-display')).not.toBeNull();
  });
  it('conserva texto, tolera fórmulas inválidas y no ejecuta HTML ni comandos confiables', () => {
    const fixture = TestBed.createComponent(MathHost);
    fixture.componentInstance.text.set(String.raw`<img src=x onerror=alert(1)> $\frac{$`);
    expect(() => fixture.detectChanges()).not.toThrow();
    expect(fixture.nativeElement.querySelector('img')).toBeNull();
    expect(fixture.nativeElement.textContent).toContain('<img');
    fixture.componentInstance.text.set(String.raw`$\href{javascript:alert(1)}{abrir}$`);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('a')).toBeNull();
  });
});
