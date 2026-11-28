export interface WikipediaSource {
  provider: 'wikipedia_es';
  page_id: number;
  revision_id: number;
  title: string;
  url: string;
  revision_at: string;
  retrieved_at: string;
  license_name: string;
  license_url: string;
  attribution: string;
  text_sha256: string;
  snapshot_sha256: string;
  extraction_version: string;
}
export interface WikiResult { page_id: number; title: string }
export interface WikiPreview { source: WikipediaSource; text: string; warnings: string[] }

export interface CoreResult { work_id: number; title: string; authors: string[]; year: number | null; language: string | null }
export interface CorePreview extends CoreResult { url: string; abstract: string; record_sha256: string; retrieved_at: string; license_statement: string; full_text_available: boolean }
export interface CoreSource {
  provider: 'core'; work_id: number; title: string; url: string; authors: string[]; year: number | null;
  retrieved_at: string; license_name: string; attribution: string; record_sha256: string;
  snapshot_sha256: string; extraction_version: string; content_origin: 'teacher_uploaded_original';
}
export type ExternalSource = WikipediaSource | CoreSource;
