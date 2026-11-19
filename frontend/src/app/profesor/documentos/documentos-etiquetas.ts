import { CourseDocument } from './documentos.model';

export function processingLabel(document: CourseDocument, processingId: string | null) {
  if (processingId === document.id) return 'Extrayendo y segmentando…';
  switch (document.processing_status) {
    case 'processing':
      return 'Procesamiento en curso';
    case 'processed':
      return `${document.chunk_count} ${document.chunk_count === 1 ? 'fragmento' : 'fragmentos'} · Texto procesado`;
    case 'failed':
      return 'No se pudo procesar · Puedes reintentar';
    default:
      return 'Guardado · Pendiente de procesamiento';
  }
}

export function indexLabel(document: CourseDocument) {
  switch (document.index_status) {
    case 'indexed':
      return 'Índice preparado';
    case 'indexing':
      return 'Preparando índice…';
    case 'failed':
      return 'Índice con error';
    default:
      return 'Índice pendiente';
  }
}
