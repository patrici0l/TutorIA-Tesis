import { TestBed } from '@angular/core/testing';
import { ResourceViewComponent } from './resource-view.component';

describe('Recurso generado', () => {
  it('renderiza texto y citas sin activar HTML', async () => {
    const fixture = TestBed.createComponent(ResourceViewComponent);
    const block = { text: '<script>no ejecutar</script>', citations: ['S1'] };
    fixture.componentRef.setInput('resource', {
      resource_type: 'EXPLANATION',
      title: 'Explicación',
      summary: block,
      steps: [block],
      worked_example: block,
    });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain(block.text);
    expect(fixture.nativeElement.textContent).toContain('Fuentes: S1');
    expect(fixture.nativeElement.querySelector('script')).toBeNull();
  });
});
