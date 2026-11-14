import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ResourceExportService } from './exportar.service';
import { HistoryDetail } from './historial.model';

describe('Descarga local del historial', () => {
  const detail: HistoryDetail = {
    preparation: {
      id: 'c3ab007f-b3ba-472e-a805-39312ec0a29e',
      status: 'prepared',
      topic: 'Derivadas',
      learning_objective: 'Explicar x²',
      resource_type: 'EXPLANATION',
      difficulty: 'basic',
      question_count: null,
      adaptation: null,
      sources: [
        {
          id: 'source',
          citation_id: 'S1',
          document_id: 'doc',
          document_title: 'Fuente sintética',
          filename: 'fuente.txt',
          source_kind: 'paragraph',
          source_index: 1,
          position: 0,
          char_start: 0,
          char_end: 12,
          text: 'x² · ñ <script>no ejecutar</script>',
          document_sha256: 'a'.repeat(64),
          source_sha256: 'b'.repeat(64),
          processing_version: 'text-v1',
          similarity: 0,
        },
      ],
    },
    status: 'failed',
    created_at: '2026-10-10T00:00:00Z',
    completed_at: '2026-10-10T00:01:00Z',
    resource: null,
    message: null,
    audit: null,
  };
  let create: ReturnType<typeof vi.fn>;
  let revoke: ReturnType<typeof vi.fn>;
  let click: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] });
    create = vi.fn(() => 'blob:local-export');
    revoke = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: create, revokeObjectURL: revoke });
    click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
  });
  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    TestBed.inject(HttpTestingController).verify();
  });

  it('conserva el detalle, UTF-8, cero y null sin HTTP ni HTML ejecutable', async () => {
    const before = JSON.stringify(detail);
    TestBed.inject(ResourceExportService).download(detail);
    const file = create.mock.calls[0][0] as Blob;
    expect(file.type).toBe('application/json;charset=utf-8');
    const text = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
    expect(JSON.parse(text)).toEqual(detail);
    expect(JSON.stringify(detail)).toBe(before);
    expect(document.querySelector('script')).toBeNull();
    expect(document.querySelector('a[download]')).toBeNull();
    TestBed.inject(HttpTestingController).expectNone(() => true);
  });

  it('usa nombre con UUID y libera la URL después del clic', () => {
    let filename = '';
    click.mockImplementation(function (this: HTMLAnchorElement) {
      filename = this.download;
    });
    TestBed.inject(ResourceExportService).download(detail);
    expect(filename).toBe(`prototipo-recurso-${detail.preparation.id}.json`);
    expect(revoke).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1000);
    expect(revoke).toHaveBeenCalledExactlyOnceWith('blob:local-export');
  });

  it('libera la URL y retira el enlace si el navegador rechaza el clic', () => {
    click.mockImplementation(() => {
      throw new Error('Download unavailable');
    });
    expect(() => TestBed.inject(ResourceExportService).download(detail)).toThrow();
    expect(revoke).toHaveBeenCalledExactlyOnceWith('blob:local-export');
    expect(document.querySelector('a[download]')).toBeNull();
  });

  it('rechaza un identificador inválido antes de crear un archivo', () => {
    const invalid = { ...detail, preparation: { ...detail.preparation, id: '../../private' } };
    expect(() => TestBed.inject(ResourceExportService).download(invalid)).toThrow();
    expect(create).not.toHaveBeenCalled();
    expect(click).not.toHaveBeenCalled();
  });
});
