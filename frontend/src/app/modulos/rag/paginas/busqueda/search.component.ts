import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { SearchResponse } from '../../modelos/search.model';
import { SearchService } from '../../servicios/search.service';

@Component({
  selector: 'app-source-search',
  imports: [FormsModule, DecimalPipe, RouterLink],
  templateUrl: './search.component.html',
  styleUrl: './search.component.scss',
})
export class SearchComponent {
  private readonly service = inject(SearchService);
  private readonly auth = inject(AuthService);
  private readonly destroy = inject(DestroyRef);
  readonly canSearch = computed(() => ['teacher', 'admin'].includes(this.auth.user()?.rol ?? ''));
  readonly loading = signal(false);
  readonly error = signal('');
  readonly response = signal<SearchResponse | null>(null);
  query = '';
  topK = 5;
  minSimilarity = 0;

  search() {
    if (!this.canSearch() || this.loading()) return;
    const query = this.query.trim();
    if (
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
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.response.set(null);
    this.service
      .search(query, this.topK, this.minSimilarity)
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (response) => {
          this.response.set(response);
          this.loading.set(false);
        },
        error: (error: HttpErrorResponse) => {
          this.error.set(
            typeof error.error?.detail === 'string'
              ? error.error.detail
              : 'No se pudo buscar. Revisa la conexión y vuelve a intentarlo.',
          );
          this.loading.set(false);
        },
      });
  }
}
