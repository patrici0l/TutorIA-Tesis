import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../inicio/sesion.service';

@Component({
  selector: 'app-class-simulation',
  imports: [FormsModule, RouterLink],
  templateUrl: './simulacion.html',
  styleUrl: './simulacion.scss'
})
export class ClassSimulationComponent {
  readonly auth = inject(AuthService);
  readonly students = signal<{email: string; group: string; nombre: string; apellido: string}[]>([]);
  readonly rosterStatus = signal<'loading' | 'ready' | 'error'>('loading');
  group: 'G3' | 'G24' = 'G3';
  individual = false;
  query = '';
  student = '';
  scenario: 'refuerzo' | 'practica' | 'reto' | 'pendiente' | '' = '';
  preview = false;

  readonly supports = [
    {id: 'refuerzo', label: 'Refuerzo paso a paso', hint: 'Empezar con un ejemplo resuelto.'},
    {id: 'practica', label: 'Práctica guiada', hint: 'Resolver con apoyo y comprobar el resultado.'},
    {id: 'reto', label: 'Reto autónomo', hint: 'Variar el problema y justificar una solución propia.'},
    {id: 'pendiente', label: 'Diagnóstico inicial', hint: 'Explorar qué sabe el estudiante antes de elegir un apoyo.'},
  ] as const;

  ngOnInit() {
    if (this.auth.mode() === 'mock' && ['teacher', 'admin'].includes(this.auth.user()?.rol ?? '')) {
      this.loadStudents();
    }
  }
  loadStudents() {
    this.rosterStatus.set('loading');
    this.auth.students().subscribe({
      next: rows => { this.students.set(rows); this.rosterStatus.set('ready'); },
      error: () => this.rosterStatus.set('error')
    });
  }
  resetRecipient() {
    this.query = '';
    this.student = '';
    this.preview = false;
  }
  get matches() {
    const normalize = (value: string) => value.toLocaleLowerCase('es').normalize('NFD').replace(/\p{M}/gu, '');
    const query = normalize(this.query.trim());
    return this.students().filter(person => person.group === this.group &&
      normalize(person.email).includes(query));
  }
  get recipient() {
    const person = this.students().find(p => p.email === this.student && p.group === this.group);
    return this.individual && person ? person.email : 'Todo el grupo';
  }
  get supportLabel() { return this.supports.find(s => s.id === this.scenario)?.label; }
  get exercise() {
    if (this.scenario !== 'pendiente') return this.groups[this.group].exercise;
    return this.group === 'G3' ? '¿Cómo identificarías la cantidad inicial y el cambio por minuto en un problema de volumen?' :
      '¿Qué relación hay entre las pendientes de dos rectas perpendiculares?';
  }
  readonly groups = {
    G3: {size: 36, topic: 'modelación lineal', exercise: 'Un depósito contiene 90 litros y pierde 3 litros por minuto. Expresa el volumen en función del tiempo e indica hasta cuándo vale el modelo.'},
    G24: {size: 34, topic: 'perpendicularidad y distancia', exercise: 'Dibuja la recta y = 2x y el punto (0, 5). Encuentra el pie de la perpendicular y calcula la distancia.'}
  };
  readonly activities = {
    refuerzo: 'El docente resuelve primero un ejemplo análogo y pide identificar los datos y justificar el primer paso del ejercicio.',
    practica: 'Resolver el ejercicio en parejas y comprobar el resultado por sustitución.',
    reto: 'Resolver de forma autónoma, variar un dato y explicar cómo cambia el resultado.',
    pendiente: 'Proponer una pregunta diagnóstica breve antes de elegir el tipo de apoyo.'
  };
}
