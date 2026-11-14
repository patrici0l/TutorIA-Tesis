export interface NavigationItem {
  path: string;
  label: string;
  description: string;
}
const common: NavigationItem[] = [
  { path: '/inicio', label: 'Inicio', description: 'Tu espacio de trabajo' },
];
const student: NavigationItem[] = [
  {
    path: '/actividades',
    label: 'Actividades asignadas',
    description: 'Ejercicios y materiales de tu profesor',
  },
  {
    path: '/practica',
    label: 'Práctica libre',
    description: 'Repaso voluntario con historial personal',
  },
];
const teacher: NavigationItem[] = [
  {
    path: '/documentos',
    label: 'Mis documentos',
    description: 'Sube y prepara tus materiales de clase',
  },
  {
    path: '/recursos',
    label: 'Recursos',
    description: 'Crea recursos o retoma los que guardaste',
  },
  {
    path: '/actividades',
    label: 'Actividades asignadas',
    description: 'Asigna contenido y consulta resultados',
  },
  {
    path: '/busqueda',
    label: 'Buscar fuentes',
    description: 'Consulta tus documentos preparados',
  },
  {
    path: '/perfiles',
    label: 'Perfiles de aprendizaje',
    description: 'Apoyo opcional para adaptar un recurso',
  },
  {
    path: '/metricas',
    label: 'Uso de generación',
    description: 'Consulta solicitudes, tokens y tiempos de generación',
  },
];
export function navigationItems(role: string): NavigationItem[] {
  return [
    ...common,
    ...(role === 'student' ? student : role === 'teacher' || role === 'admin' ? teacher : []),
  ];
}
