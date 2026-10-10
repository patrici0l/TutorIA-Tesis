export interface User {
  id: string;
  institutional_email: string;
  institutional_id: string | null;
  nombre: string;
  apellido: string;
  rol: 'admin' | 'teacher' | 'student';
  activo: boolean;
  created_at: string;
  last_login: string;
}
export interface SessionResponse {
  user: User;
  auth_mode: 'mock' | 'cas';
}
