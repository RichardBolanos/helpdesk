import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoginResponse, Role, User } from './models';

const TOKEN_KEY = 'token';
const USER_KEY = 'user';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);

  readonly token = signal<string | null>(this.validToken());
  readonly user = signal<User | null>(
    this.token() ? JSON.parse(localStorage.getItem(USER_KEY) ?? 'null') : null,
  );
  readonly isLoggedIn = computed(() => !!this.token() && !!this.user());

  login(email: string, password: string) {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, { email, password })
      .pipe(tap((r) => this.setSession(r)));
  }

  register(name: string, email: string, password: string) {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, { name, email, password });
  }

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this.token.set(null);
    this.user.set(null);
    this.router.navigate(['/login']);
  }

  hasRole(...roles: Role[]) {
    const u = this.user();
    return !!u && roles.includes(u.role);
  }

  private setSession(r: LoginResponse) {
    localStorage.setItem(TOKEN_KEY, r.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(r.user));
    this.token.set(r.access_token);
    this.user.set(r.user);
  }

  /** Devuelve el token guardado solo si el JWT no ha expirado. */
  private validToken(): string | null {
    const t = localStorage.getItem(TOKEN_KEY);
    if (!t) return null;
    try {
      const payload = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      if (JSON.parse(atob(payload)).exp * 1000 > Date.now()) return t;
    } catch {
      // token malformado: se descarta
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    return null;
  }
}
