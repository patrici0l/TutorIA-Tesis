import { Component, input } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HistoryDetail } from '../../modelos/history.model';

@Component({
  selector: 'app-resource-audit',
  imports: [DatePipe],
  templateUrl: './resource-audit.component.html',
  styleUrl: './resource-audit.component.scss',
})
export class ResourceAuditComponent {
  readonly detail = input.required<HistoryDetail>();
  readonly statusLabels = {
    prepared: 'Preparado',
    generating: 'En proceso',
    succeeded: 'Generado',
    failed: 'Con fallo',
  };
  readonly tokens = [
    { key: 'input_tokens', label: 'Tokens de entrada' },
    { key: 'output_tokens', label: 'Tokens de salida' },
    { key: 'total_tokens', label: 'Total reportado' },
    { key: 'reasoning_tokens', label: 'Tokens de razonamiento' },
    { key: 'cached_input_tokens', label: 'Entrada en caché' },
  ] as const;
}
