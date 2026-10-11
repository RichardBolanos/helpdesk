import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { Role, User } from '../../core/models';

@Component({
  imports: [FormsModule],
  selector: 'app-users',
  styleUrl: './users.css',
  templateUrl: './users.html',
})
export class Users {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  users = signal<User[]>([]);
  error = signal('');

  constructor() {
    this.load();
  }

  isMe(u: User) {
    return u.id === this.auth.user()?.id;
  }

  load() {
    this.api.users().subscribe({
      next: (u) => this.users.set(u),
      error: () => this.error.set('No se pudieron cargar los usuarios'),
    });
  }

  update(u: User, data: { role?: Role; is_active?: boolean }) {
    this.api.updateUser(u.id, data).subscribe({
      next: (n) => this.users.update((list) => list.map((x) => (x.id === n.id ? n : x))),
      error: () => {
        this.error.set('No se pudo actualizar el usuario');
        this.load();
      },
    });
  }
}
