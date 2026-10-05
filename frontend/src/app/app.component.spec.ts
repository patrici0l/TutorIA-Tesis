import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app.component';

describe('App', () => {
  it('muestra navegación y acceso al contenido', async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([])],
    }).compileComponents();
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('a[href="#contenido"]')).toBeTruthy();
    expect(fixture.nativeElement.textContent).toContain('TutorIA');
  });
});
