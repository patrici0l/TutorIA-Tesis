import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../../inicio/sesion.service';
import { CoreSourcesComponent } from './fuentes-core';
import { CourseCatalogService } from './asignaturas.service';

describe('Fuentes CORE', () => {
  let http: HttpTestingController;
  const user = signal({ rol: 'teacher' });
  beforeEach(() => {
    user.set({ rol: 'teacher' });
    TestBed.configureTestingModule({ imports: [CoreSourcesComponent], providers: [provideRouter([]),
      provideHttpClient(), provideHttpClientTesting(), { provide: AuthService, useValue: { user } },
      { provide: CourseCatalogService, useValue: { load: () => of([]) } },
    ] }); http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());
  it('muestra el resumen como ficha y exige un original para incorporar', () => {
    const f = TestBed.createComponent(CoreSourcesComponent), c = f.componentInstance;
    c.query = 'probabilidad'; c.search();
    http.expectOne('/api/v1/documents/external/core/search?q=probabilidad').flush([{work_id:42,title:'Tema',authors:[]}]);
    c.review(c.results()[0]);
    http.expectOne('/api/v1/documents/external/core/preview/42').flush({work_id:42,title:'Tema',authors:[],abstract:'<script>no ejecutar</script>',record_sha256:'a'.repeat(64),full_text_available:false});
    f.detectChanges();
    expect(f.nativeElement.querySelector('script')).toBeNull();
    expect(f.nativeElement.textContent).toContain('El resumen no se importará');
    c.course = 'Cálculo'; c.confirmed = true; c.permission = 'Permiso propio de prueba';
    c.importOriginal(); http.expectNone('/api/v1/documents/external/core/import');
    c.file.set(new File(['Texto original'], 'original.txt', {type:'text/plain'})); c.importOriginal(); c.importOriginal();
    const req = http.expectOne('/api/v1/documents/external/core/import');
    expect(req.request.body.get('work_id')).toBe('42');
    expect(req.request.body.get('abstract')).toBeNull();
    req.flush({id:'doc',course:'cálculo'}); f.detectChanges();
    expect(f.nativeElement.textContent).toContain('Original guardado');
  });
  it('limpia archivo, permiso y confirmación al elegir otra publicación', () => {
    const c = TestBed.createComponent(CoreSourcesComponent).componentInstance;
    c.file.set(new File(['x'], 'x.txt')); c.permission='Permiso'; c.confirmed=true;
    c.review({work_id:43,title:'Otro',authors:[],year:null,language:null});
    expect(c.file()).toBeNull(); expect(c.permission).toBe(''); expect(c.confirmed).toBe(false);
    http.expectOne('/api/v1/documents/external/core/preview/43').flush({detail:'CORE restringió el acceso.'}, {status:503,statusText:'Unavailable'});
    expect(c.busy()).toBe(false); expect(c.error()).toContain('restringió');
  });
  it('no consulta CORE desde una sesión de estudiante', () => {
    user.set({rol:'student'});
    const c = TestBed.createComponent(CoreSourcesComponent).componentInstance; c.query='tema'; c.search();
    http.expectNone('/api/v1/documents/external/core/search?q=tema');
  });
});
