import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';
import { User } from './models';

const user: User = { id: 1, name: 'Ana', email: 'ana@example.com', role: 'agent', is_active: true };

/** JWT de mentira: solo importa el payload con la fecha de expiración. */
function fakeJwt(expSecondsFromNow: number) {
  const exp = Math.floor(Date.now() / 1000) + expSecondsFromNow;
  return `header.${btoa(JSON.stringify({ sub: '1', exp }))}.signature`;
}

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;

  function setup() {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([{ path: 'login', children: [] }]),
      ],
    });
    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  }

  beforeEach(() => localStorage.clear());

  it('should be created', () => {
    setup();
    expect(service).toBeTruthy();
  });

  it('starts logged out when there is no stored session', () => {
    setup();
    expect(service.isLoggedIn()).toBe(false);
    expect(service.hasRole('admin')).toBe(false);
  });

  it('login stores the token and the user', () => {
    setup();
    service.login('ana@example.com', 'secret123').subscribe();

    const req = http.expectOne(`${environment.apiUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ email: 'ana@example.com', password: 'secret123' });
    req.flush({ access_token: 'abc', token_type: 'bearer', user });

    expect(service.token()).toBe('abc');
    expect(service.user()).toEqual(user);
    expect(service.isLoggedIn()).toBe(true);
    expect(localStorage.getItem('token')).toBe('abc');
  });

  it('hasRole checks the role of the current user', () => {
    setup();
    service.user.set(user);
    expect(service.hasRole('agent', 'admin')).toBe(true);
    expect(service.hasRole('user')).toBe(false);
  });

  it('logout clears the session', () => {
    setup();
    service.login('ana@example.com', 'x').subscribe();
    http.expectOne(`${environment.apiUrl}/auth/login`).flush({ access_token: 'abc', token_type: 'bearer', user });

    service.logout();

    expect(service.isLoggedIn()).toBe(false);
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('restores a stored session while the JWT has not expired', () => {
    localStorage.setItem('token', fakeJwt(3600));
    localStorage.setItem('user', JSON.stringify(user));
    setup();
    expect(service.isLoggedIn()).toBe(true);
    expect(service.user()?.name).toBe('Ana');
  });

  it('discards a stored session when the JWT has expired', () => {
    localStorage.setItem('token', fakeJwt(-60));
    localStorage.setItem('user', JSON.stringify(user));
    setup();
    expect(service.isLoggedIn()).toBe(false);
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('discards a malformed stored token', () => {
    localStorage.setItem('token', 'not-a-jwt');
    setup();
    expect(service.token()).toBeNull();
  });
});
