import { Component, DestroyRef, inject, Input, OnChanges, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { GenerationQuota, PreparationService } from '../../servicios/preparation.service';

@Component({
  selector: 'app-generation-quota',
  imports: [DatePipe],
  templateUrl: './quota.html',
  styleUrl: './quota.scss',
})
export class GenerationQuotaComponent implements OnChanges {
  @Input() refresh = 0;
  private readonly service = inject(PreparationService);
  private readonly destroy = inject(DestroyRef);
  readonly quota = signal<GenerationQuota | null>(null);
  readonly loading = signal(false);
  readonly error = signal(false);
  ngOnChanges() {
    this.load();
  }
  load() {
    if (this.loading()) return;
    this.loading.set(true);
    this.error.set(false);
    this.quota.set(null);
    this.service
      .quota()
      .pipe(takeUntilDestroyed(this.destroy))
      .subscribe({
        next: (quota) => {
          this.quota.set(quota);
          this.loading.set(false);
        },
        error: () => {
          this.error.set(true);
          this.loading.set(false);
        },
      });
  }
}
