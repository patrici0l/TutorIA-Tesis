import { Component, inject, input, OnChanges, signal } from '@angular/core';
import { HistoryDetail } from '../../modelos/history.model';
import { ResourceExportService } from '../../servicios/resource-export.service';

@Component({
  selector: 'app-resource-export',
  templateUrl: './resource-export.component.html',
  styleUrl: './resource-export.component.scss',
})
export class ResourceExportComponent implements OnChanges {
  private readonly exporter = inject(ResourceExportService);
  readonly detail = input.required<HistoryDetail>();
  readonly message = signal('');
  readonly failed = signal(false);

  ngOnChanges() {
    this.message.set('');
    this.failed.set(false);
  }

  download() {
    this.message.set('');
    this.failed.set(false);
    try {
      this.exporter.download(this.detail());
      this.message.set('Se solicitó la descarga. Revisa las descargas de tu navegador.');
    } catch {
      this.failed.set(true);
      this.message.set('No se pudo descargar el recurso. Puedes volver a intentarlo.');
    }
  }
}
