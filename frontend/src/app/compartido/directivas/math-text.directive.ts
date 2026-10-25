import { Directive, ElementRef, inject, input, OnChanges } from '@angular/core';
import renderMathInElement from 'katex/contrib/auto-render';

/** The bundled engine is loaded before Angular creates this directive. */
@Directive({ selector: '[appMathText]' })
export class MathTextDirective implements OnChanges {
  readonly appMathText = input.required<string>();
  private readonly host = inject(ElementRef<HTMLElement>);

  ngOnChanges() {
    // Never interpret resource text as HTML. Only KaTeX generates markup.
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
