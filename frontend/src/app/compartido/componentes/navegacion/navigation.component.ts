import {
  afterEveryRender,
  afterNextRender,
  Component,
  computed,
  DestroyRef,
  ElementRef,
  HostListener,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AuthService } from '../../../nucleo/servicios/auth.service';

@Component({
  selector: 'app-workspace-navigation',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './navigation.component.html',
  styleUrl: './navigation.component.scss',
})
export class NavigationComponent {
  private readonly auth = inject(AuthService);
  private readonly host = inject(ElementRef<HTMLElement>);
  private readonly destroyRef = inject(DestroyRef);
  readonly track = viewChild<ElementRef<HTMLElement>>('track');
  private readonly trigger = viewChild<ElementRef<HTMLButtonElement>>('trigger');
  readonly open = signal(false);
  readonly overflow = signal(false);
  readonly atStart = signal(true);
  readonly atEnd = signal(true);
  readonly items = computed(() => {
    const user = this.auth.user();
    if (!user)
      return [
        {
          path: '/login',
          label: 'Acceso UPS',
          description: 'Entra a tu espacio de aprendizaje',
          icon: 'access',
        },
      ];
    const links = [
      {
        path: '/inicio',
        label: 'Inicio',
        description: 'Tu espacio de aprendizaje, de un vistazo',
        icon: 'home',
      },
    ];
    if (user.rol === 'teacher' || user.rol === 'admin') {
      links.push({
        path: '/perfiles',
        label: 'Perfiles',
        description: 'Revisa observaciones sintéticas de rendimiento',
        icon: 'document',
      });
      links.push({
        path: '/documentos',
        label: 'Documentos',
        description: 'Organiza los materiales de tu curso',
        icon: 'document',
      });
      links.push({
        path: '/busqueda',
        label: 'Buscar fuentes',
        description: 'Encuentra conceptos en tus materiales',
        icon: 'search',
      });
      links.push({
        path: '/recursos',
        label: 'Preparar recursos',
        description: 'Define tu recurso y revisa sus fuentes',
        icon: 'document',
      });
    }
    return links;
  });
  private revealPending = true;

  constructor() {
    inject(Router)
      .events.pipe(takeUntilDestroyed())
      .subscribe((event) => {
        if (event instanceof NavigationEnd) {
          this.open.set(false);
          this.revealPending = true;
        }
      });
    afterNextRender(() => {
      const track = this.track()?.nativeElement;
      if (track && typeof ResizeObserver !== 'undefined') {
        const observer = new ResizeObserver(() => {
          this.measure();
          this.revealActive();
        });
        observer.observe(track);
        this.destroyRef.onDestroy(() => observer.disconnect());
      }
    });
    afterEveryRender(() => {
      this.measure();
      if (this.revealPending) {
        this.revealActive();
        this.revealPending = false;
      }
    });
  }

  toggle() {
    this.open.update((value) => !value);
  }
  close() {
    this.open.set(false);
  }
  measure() {
    const track = this.track()?.nativeElement;
    if (!track) return;
    this.overflow.set(track.scrollWidth > track.clientWidth + 2);
    this.atStart.set(track.scrollLeft <= 2);
    this.atEnd.set(track.scrollLeft + track.clientWidth >= track.scrollWidth - 2);
  }
  scroll(direction: number) {
    const track = this.track()?.nativeElement;
    track?.scrollBy({
      left: direction * track.clientWidth * 0.75,
      behavior: this.scrollBehavior(),
    });
  }
  private scrollBehavior(): ScrollBehavior {
    return typeof matchMedia !== 'undefined' &&
      matchMedia('(prefers-reduced-motion: reduce)').matches
      ? 'auto'
      : 'smooth';
  }
  private revealActive() {
    const track = this.track()?.nativeElement;
    const active = track?.querySelector<HTMLElement>('[aria-current="page"]');
    if (!track || !active) return;
    const left = active.offsetLeft;
    const right = left + active.offsetWidth;
    if (left < track.scrollLeft) track.scrollTo({ left, behavior: this.scrollBehavior() });
    else if (right > track.scrollLeft + track.clientWidth)
      track.scrollTo({ left: right - track.clientWidth, behavior: this.scrollBehavior() });
  }
  @HostListener('document:click', ['$event'])
  outsideClick(event: MouseEvent) {
    if (event.target instanceof Node && !this.host.nativeElement.contains(event.target))
      this.close();
  }
  @HostListener('document:keydown.escape', ['$event'])
  escape(event: Event) {
    if (!this.open()) return;
    event.preventDefault();
    this.close();
    this.trigger()?.nativeElement.focus();
  }
  @HostListener('focusout', ['$event'])
  focusOut(event: FocusEvent) {
    if (!event.relatedTarget || !this.host.nativeElement.contains(event.relatedTarget as Node))
      this.close();
  }
}
