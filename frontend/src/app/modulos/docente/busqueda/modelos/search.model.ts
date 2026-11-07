export interface SearchHit {
  id: string;
  document_id: string;
  document_title: string;
  filename: string;
  document_sha256: string;
  source_sha256: string;
  processing_version: string;
  position: number;
  source_kind: 'page' | 'paragraph';
  source_index: number;
  char_start: number;
  char_end: number;
  text: string;
  similarity: number;
}

export interface SearchResponse {
  query: string;
  embedding_query: string;
  query_version: string;
  top_k: number;
  min_similarity: number;
  available_chunks: number;
  results: SearchHit[];
  method: 'exact_cosine';
  embedding_model: string;
  embedding_revision: string;
  embedding_version: string;
  elapsed_ms: number;
}
