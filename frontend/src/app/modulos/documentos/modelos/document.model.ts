export interface CourseDocument {
  id: string;
  filename: string;
  title: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  status: 'uploaded' | 'deleted';
  created_at: string;
  processing_status: 'pending' | 'processing' | 'processed' | 'failed';
  processing_error: string | null;
  processed_at: string | null;
  processing_started_at: string | null;
  processing_version: string | null;
  chunk_chars: number | null;
  chunk_overlap: number | null;
  chunk_count: number;
  text_chars: number;
  index_status: 'pending' | 'indexing' | 'indexed' | 'failed';
  index_error: string | null;
  index_started_at: string | null;
  indexed_at: string | null;
  embedding_model: string | null;
  embedding_revision: string | null;
  embedding_version: string | null;
}
export interface DocumentChunk {
  id: string;
  position: number;
  source_kind: 'page' | 'paragraph';
  source_index: number;
  char_start: number;
  char_end: number;
  text: string;
}
export interface DocumentChunkList {
  items: DocumentChunk[];
  total: number;
  limit: number;
  offset: number;
}
export interface DocumentList {
  items: CourseDocument[];
  total: number;
  limit: number;
  offset: number;
}
