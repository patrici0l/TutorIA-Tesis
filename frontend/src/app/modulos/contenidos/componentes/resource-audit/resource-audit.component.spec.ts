import { TestBed } from '@angular/core/testing';
import { ResourceAuditComponent } from './resource-audit.component';
import { HistoryDetail } from '../../modelos/history.model';

describe('Auditoría de recursos', () => {
  const detail: HistoryDetail = {
    preparation: {
      id: 'test',
      status: 'prepared',
      topic: 'Derivadas',
      learning_objective: 'Practicar',
      resource_type: 'EXPLANATION',
      difficulty: 'basic',
      question_count: null,
      sources: [],
    },
    status: 'failed',
    created_at: '2026-10-08T23:00:00Z',
    completed_at: '2026-10-08T23:01:00Z',
    resource: null,
    message: null,
    audit: {
      generation_started_at: null,
      provider: 'gemini',
      requested_model: 'test-model',
      model_version: null,
      prompt_version: '<script>no ejecutar</script>',
      prompt_sha256: 'a'.repeat(64),
      usage: {
        input_tokens: 0,
        output_tokens: null,
        total_tokens: null,
        reasoning_tokens: null,
        cached_input_tokens: null,
      },
      latency_ms: 0,
      estimated_cost: null,
      error_code: 'llm_timeout',
      retrieval: {
        method: 'exact_cosine',
        query_version: 'query-v1',
        embedding_model: 'test-embedding',
        embedding_revision: 'rev-test',
        embedding_version: 'e5-v1',
        top_k: 3,
        min_similarity: 0,
        available_chunks: 1,
        elapsed_ms: 1,
      },
    },
  };
  it('conserva cero conocido y ausencias, muestra fallo seguro y escapa metadatos', async () => {
    TestBed.configureTestingModule({ imports: [ResourceAuditComponent] });
    const fixture = TestBed.createComponent(ResourceAuditComponent);
    fixture.componentRef.setInput('detail', detail);
    fixture.detectChanges();
    await fixture.whenStable();
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('llm_timeout');
    expect(text).toContain('0 ms');
    expect(text).toContain('Desconocido');
    expect(text).toContain('Sin fecha registrada');
    expect(text).toContain('<script>no ejecutar</script>');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
    expect(text).toContain('rev-test');
  });
  it('no inventa auditoría cuando un cliente antiguo no incluye datos', () => {
    TestBed.configureTestingModule({ imports: [ResourceAuditComponent] });
    const fixture = TestBed.createComponent(ResourceAuditComponent);
    fixture.componentRef.setInput('detail', { ...detail, audit: null });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('details')).toBeNull();
  });
});
