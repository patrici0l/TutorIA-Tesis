import { Component, input } from '@angular/core';
import { CitedText, EducationalResource } from '../../modelos/preparation.model';

@Component({
  selector: 'app-resource-view',
  templateUrl: './resource-view.component.html',
  styleUrl: './resource-view.component.scss',
})
export class ResourceViewComponent {
  readonly resource = input.required<EducationalResource>();
  sections(): { heading: string; blocks: CitedText[] }[] {
    const r = this.resource();
    switch (r.resource_type) {
      case 'EXPLANATION':
        return [
          { heading: 'Concepto', blocks: [r.summary] },
          { heading: 'Paso a paso', blocks: r.steps },
          { heading: 'Ejemplo resuelto', blocks: [r.worked_example] },
        ];
      case 'EXERCISE':
        return [
          { heading: 'Enunciado', blocks: [r.statement] },
          { heading: 'Pistas', blocks: r.hints },
          { heading: 'Solución guiada', blocks: r.solution_steps },
          { heading: 'Resultado', blocks: [r.answer] },
        ];
      case 'FEEDBACK':
        return [
          { heading: 'Revisión', blocks: [r.diagnosis] },
          { heading: 'Corrección', blocks: [r.correction] },
          { heading: 'Siguiente paso', blocks: [r.next_step] },
        ];
      case 'QUIZ':
        return [];
    }
  }
}
