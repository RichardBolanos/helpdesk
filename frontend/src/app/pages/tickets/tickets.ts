import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { Priority, Ticket, TicketStatus } from '../../core/models';

@Component({
  imports: [FormsModule, DatePipe],
  selector: 'app-tickets',
  styleUrl: './tickets.css',
  templateUrl: './tickets.html',
})
export class Tickets {
  private api = inject(ApiService);
  protected auth = inject(AuthService);

  tickets = signal<Ticket[]>([]);
  error = signal('');

  title = '';
  description = '';
  priority: Priority = 'medium';

  constructor() {
    this.load();
  }

  load() {
    this.api.tickets().subscribe({
      next: (t) => this.tickets.set(t),
      error: () => this.error.set('No se pudieron cargar los tickets'),
    });
  }

  create() {
    this.api
      .createTicket({ title: this.title, description: this.description, priority: this.priority })
      .subscribe({
        next: (t) => {
          this.tickets.update((list) => [t, ...list]);
          this.title = this.description = '';
          this.priority = 'medium';
        },
        error: () => this.error.set('No se pudo crear el ticket'),
      });
  }

  setStatus(t: Ticket, status: TicketStatus) {
    this.api.updateTicketStatus(t.id, status).subscribe({
      next: (u) => this.tickets.update((list) => list.map((x) => (x.id === u.id ? u : x))),
      error: () => {
        this.error.set('No se pudo actualizar el estado');
        this.load();
      },
    });
  }

  remove(t: Ticket) {
    if (!confirm(`¿Borrar el ticket #${t.id}?`)) return;
    this.api.deleteTicket(t.id).subscribe({
      next: () => this.tickets.update((list) => list.filter((x) => x.id !== t.id)),
      error: () => this.error.set('No se pudo borrar el ticket'),
    });
  }
}
