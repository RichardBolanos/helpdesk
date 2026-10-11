import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  imports: [FormsModule, RouterLink],
  selector: 'app-register',
  styleUrl: './register.css',
  templateUrl: './register.html',
})
export class Register {
  private auth = inject(AuthService);
  private router = inject(Router);

  name = '';
  email = '';
  password = '';
  loading = signal(false);
  error = signal('');

  submit() {
    this.loading.set(true);
    this.error.set('');
    this.auth.register(this.name, this.email, this.password).subscribe({
      next: () => this.router.navigate(['/login']),
      error: (e) => {
        this.error.set(
          e.status === 409
            ? 'Ese email ya está registrado'
            : e.status === 0
              ? 'No se pudo conectar con el servidor'
              : 'Datos inválidos: revisa el email y usa una contraseña de 8 a 72 caracteres',
        );
        this.loading.set(false);
      },
    });
  }
}
