import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { environment } from '../../environments/environment';
import { Priority, Role, Ticket, TicketStatus, User } from './models';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private http = inject(HttpClient);
  private url = environment.apiUrl;

  tickets() {
    return this.http.get<Ticket[]>(`${this.url}/tickets`);
  }
  createTicket(data: { title: string; description: string; priority: Priority }) {
    return this.http.post<Ticket>(`${this.url}/tickets`, data);
  }
  updateTicketStatus(id: number, status: TicketStatus) {
    return this.http.patch<Ticket>(`${this.url}/tickets/${id}`, { status });
  }
  deleteTicket(id: number) {
    return this.http.delete<void>(`${this.url}/tickets/${id}`);
  }

  users() {
    return this.http.get<User[]>(`${this.url}/users`);
  }
  updateUser(id: number, data: { role?: Role; is_active?: boolean }) {
    return this.http.patch<User>(`${this.url}/users/${id}`, data);
  }
}
