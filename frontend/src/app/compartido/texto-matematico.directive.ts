import { Directive, ElementRef, inject, input, OnChanges } from '@angular/core';
import renderMathInElement from 'katex/contrib/auto-render';

/** KaTeX se carga antes de crear la vista y procesa cada cambio de texto. */
@Directive({ selector: '[appMathText]' })
export class MathTextDirective implements OnChanges {
  readonly appMathText = input.required<string>();
  private readonly host = inject(ElementRef<HTMLElement>);

  ngOnChanges() {
    // El recurso entra como texto; solo KaTeX genera el marcado matemático.
    const element = this.host.nativeElement;
    element.textContent = this.appMathText();
    renderMathInElement(element, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '\\(', right: '\\)', display: false },
        { left: '$', right: '$', display: false },
      ],
      throwOnError: false,
      trust: false,
      maxExpand: 1000,
      maxSize: 20,
    });
  }
}
