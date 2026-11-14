import { EducationalResource, PreparationResponse } from '../recursos/recursos.model';
export type AssignmentStatus = 'open' | 'closed' | 'cancelled';
export const ASSIGNMENT_STATUS_LABELS: Record<AssignmentStatus, string> = {
  open: 'Abierta',
  closed: 'Cerrada',
  cancelled: 'Cancelada',
};

export interface Assignment {
  id: string;
  version: string;
  title: string;
  instructions: string;
  student_email: string;
  created_at: string;
  status: AssignmentStatus;
  status_changed_at: string | null;
  attempts: number;
  best_score: number | null;
  resource_id?: string | null;
  resource?: EducationalResource | null;
  sources?: PreparationResponse['sources'];
}
export interface AssignmentPage {
  items: Assignment[];
  total: number;
  offset: number;
  limit: number;
}
export interface AssignmentSubmission {
  resource_id?: string;
  id: string;
  student_email: string;
  version: string;
  title: string;
  instructions: string;
}
