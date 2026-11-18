import { ViewAttention } from '../../compartido/atencion-vista.service';
// Consulta fuentes propias y retira resultados anteriores al iniciar otra búsqueda.
import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../inicio/sesion.service';
import { SearchResponse } from './busqueda.model';
import { SearchService } from './busqueda.service';

@Component({
  selector: 'app-source-search',
  imports: [FormsModule, DecimalPipe, RouterLink],
  templateUrl: './busqueda.html',
  styleUrl: './busqueda.scss',
})
export class SearchComponent {
  private readonly attention = inject(ViewAttention);
  private readonly service = inject(SearchService);
  private readonly auth = inject(AuthService);
  private readonly destroy = inject(DestroyRef);
  readonly canSearch = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly loading = signal(false);
  readonly error = signal('');
  readonly response = signal<SearchResponse | null>(null);
  readonly resultOffset = signal(0);
  readonly visibleResults = computed(() => this.response()?.results.slice(this.resultOffset(), this.resultOffset() + 5) ?? []);
  pageResults(offset: number) {
    this.resultOffset.set(offset);
    this.attention.reveal('results-title');
  }
  course = '';
  query = '';
  topK = 5;
  minSimilarity = 0;

  search() {
    if (!this.canSearch() || this.loading()) return;
    const query = this.query.trim();
    if (
      !this.course.trim() ||
      this.course.trim().length > 160 ||
      !query ||
      query.length > 1000 ||
      !Number.isInteger(this.topK) ||
      this.topK < 1 ||
      this.topK > 10 ||
      !Number.isFinite(this.minSimilarity) ||
      this.minSimilarity < 0 ||
      this.minSimilarity > 1
    ) {
      this.error.set('Escribe una consulta y revisa los límites de búsqueda.');
      this.attention.reveal('search-error');
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.response.set(null);
    this.resultOffset.set(0);
    this.service
      .search(query, this.topK, this.minSimilarity, this.course.trim())
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.response.set(response);
          this.loading.set(false);
          this.attention.reveal('results-title');
        },
        error: (error: HttpErrorResponse) => {
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo buscar. Revisa la conexión y vuelve a intentarlo.',
          );
          this.loading.set(false);
          this.attention.reveal('search-error');
        },
      });
  }
}
