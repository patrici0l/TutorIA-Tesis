// Exporta una copia local del recurso y su trazabilidad sin volver a generar.
import { DOCUMENT } from '@angular/common';
import { inject, Injectable } from '@angular/core';
import { HistoryDetail } from './historial.model';

@Injectable({ providedIn: 'root' })
export class ResourceExportService {
  private readonly document = inject(DOCUMENT);

  download(detail: HistoryDetail) {
    const id = detail.preparation.id;
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
      throw new Error('Identificador de recurso inválido.');
    }
    // Export the detail already authorized by the API, preserving null and zero.
    const file = new Blob([JSON.stringify(detail, null, 2) + '\n'], {
      type: 'application/json;charset=utf-8',
    });
    const url = URL.createObjectURL(file);
    const link = this.document.createElement('a');
    try {
      link.href = url;
      link.download = `prototipo-recurso-${id}.json`;
      link.hidden = true;
      this.document.body.appendChild(link);
      link.click();
    } catch (error) {
      URL.revokeObjectURL(url);
      throw error;
    } finally {
      link.remove();
    }
    // Give the browser time to start the download before releasing the local URL.
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}
