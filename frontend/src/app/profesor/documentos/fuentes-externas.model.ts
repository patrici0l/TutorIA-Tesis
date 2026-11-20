export interface ExternalSource {
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
export interface WikiPreview { source: ExternalSource; text: string; warnings: string[] }
