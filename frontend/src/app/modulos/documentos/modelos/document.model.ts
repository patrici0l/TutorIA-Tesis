export interface CourseDocument {
  id: string;
  filename: string;
  title: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  status: 'uploaded';
  created_at: string;
}
export interface DocumentList {
  items: CourseDocument[];
  total: number;
  limit: number;
  offset: number;
}
