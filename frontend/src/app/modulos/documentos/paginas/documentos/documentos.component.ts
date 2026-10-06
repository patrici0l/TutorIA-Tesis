import { Component, inject, OnInit, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../../nucleo/servicios/auth.service';
import { DocumentService } from '../../servicios/document.service';
import { CourseDocument } from '../../modelos/document.model';

@Component({
  selector: 'app-documents',
  imports: [FormsModule, DatePipe],
  templateUrl: './documentos.component.html',
  styleUrl: './documentos.component.scss',
})
export class DocumentsComponent implements OnInit {
  readonly auth = inject(AuthService);
  private readonly service = inject(DocumentService);
  readonly documents = signal<CourseDocument[]>([]);
  readonly selected = signal<CourseDocument | null>(null);
  readonly pendingDelete = signal<CourseDocument | null>(null);
  readonly loading = signal(false);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly success = signal('');
  readonly total = signal(0);
  readonly offset = signal(0);
  readonly file = signal<File | null>(null);
  title = '';
  canManage() {
    return ['teacher', 'admin'].includes(this.auth.user()?.rol ?? '');
  }
  ngOnInit() {
    if (this.canManage()) this.load();
  }
  load(offset = this.offset()) {
    this.loading.set(true);
    this.error.set('');
    this.service.list(offset).subscribe({
      next: (page) => {
        this.documents.set(page.items);
        this.total.set(page.total);
        this.offset.set(offset);
        this.loading.set(false);
      },
      error: (error) => {
        this.error.set(this.message(error));
        this.loading.set(false);
      },
    });
  }
  choose(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.error.set('');
    this.success.set('');
    this.file.set(null);
    if (!file) return;
    if (!/\.(pdf|docx|txt)$/i.test(file.name) || file.size === 0 || file.size > 10_485_760) {
      this.error.set('Selecciona un PDF, DOCX o TXT no vacío de hasta 10 MiB.');
      input.value = '';
      return;
    }
    this.file.set(file);
    if (!this.title) this.title = file.name.replace(/\.[^.]+$/, '').slice(0, 160);
  }
  upload(input: HTMLInputElement) {
    const file = this.file();
    if (!file || !this.title.trim() || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service.upload(file, this.title.trim()).subscribe({
      next: () => {
        this.busy.set(false);
        this.file.set(null);
        this.title = '';
        input.value = '';
        this.success.set('Documento guardado. Disponible para la próxima etapa de procesamiento.');
        this.load(0);
      },
      error: (error) => {
        this.error.set(this.message(error));
        this.busy.set(false);
      },
    });
  }
  view(document: CourseDocument) {
    this.error.set('');
    this.service.get(document.id).subscribe({
      next: (item) => this.selected.set(item),
      error: (error) => this.error.set(this.message(error)),
    });
  }
  remove() {
    const document = this.pendingDelete();
    if (!document || this.busy()) return;
    this.busy.set(true);
    this.error.set('');
    this.success.set('');
    this.service.delete(document.id).subscribe({
      next: () => {
        this.busy.set(false);
        this.pendingDelete.set(null);
        this.selected.set(null);
        this.success.set('Documento eliminado.');
        this.load(
          this.documents().length === 1 && this.offset() > 0 ? this.offset() - 20 : this.offset(),
        );
      },
      error: (error) => {
        this.error.set(this.message(error));
        this.busy.set(false);
      },
    });
  }
  size(bytes: number) {
    return `${(bytes / 1024).toFixed(1)} KiB`;
  }
  private message(error: HttpErrorResponse) {
    const detail = error.error?.detail;
    return typeof detail === 'string'
      ? detail
      : 'No se pudo completar la operación. Revisa la conexión e inténtalo de nuevo.';
  }
}
