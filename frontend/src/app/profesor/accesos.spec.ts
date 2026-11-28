import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { AuthService } from '../inicio/sesion.service';
import { LearningAccessComponent } from './accesos';
import { CourseCatalogService } from './documentos/asignaturas.service';

describe('Gestión de acceso', () => {
  let http: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({ imports:[LearningAccessComponent], providers:[provideHttpClient(),provideHttpClientTesting(),
      {provide:AuthService,useValue:{user:signal({rol:'teacher'})}},
      {provide:CourseCatalogService,useValue:{load:()=>of([{value:'cálculo',label:'Cálculo',enabled:0,documents:1}])}},
    ] }); http=TestBed.inject(HttpTestingController);
  });
  afterEach(()=>http.verify());
  it('distingue carga y error de una lista realmente vacía',()=>{
    const c=TestBed.createComponent(LearningAccessComponent).componentInstance;
    expect(c.loading()).toBe(true); expect(c.loaded()).toBe(false);
    http.expectOne('/api/v1/learning/access').flush({}, {status:503,statusText:'Unavailable'});
    expect(c.loaded()).toBe(false); expect(c.loading()).toBe(false); expect(c.error()).not.toBe('');
  });
  it('filtra por estado y correo sin cambiar permisos',()=>{
    const c=TestBed.createComponent(LearningAccessComponent).componentInstance;
    http.expectOne('/api/v1/learning/access').flush([
      {id:'a',course:'cálculo',student_email:'ana@example.org',active:true},
      {id:'b',course:'estadística',student_email:'bea@example.org',active:false},
    ]);
    expect(c.visible().length).toBe(1); expect(c.activeCount()).toBe(1);
    c.filter.set('all'); c.search.set('bea'); expect(c.visible()[0].id).toBe('b');
    c.course='cálculo'; expect(c.selectedCourse()?.enabled).toBe(0);
  });
});
