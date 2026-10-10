import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app.component';
import { provideHttpClient } from '@angular/common/http';

describe('App', () => {
  it('muestra navegación y acceso al contenido', async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient()],
    }).compileComponents();
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('.skip-link')).toBeTruthy();
    expect(fixture.nativeElement.textContent).toContain('TutorIA');
  });
});
