import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from './auth.service';
import { authInterceptor } from './auth-interceptor';

describe('authInterceptor', () => {
  let client: HttpClient;
  let http: HttpTestingController;
  let auth: AuthService;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        provideRouter([{ path: 'login', children: [] }]),
      ],
    });
    client = TestBed.inject(HttpClient);
    http = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
  });

  afterEach(() => http.verify());

  it('adds the Bearer header when there is a token', () => {
    auth.token.set('abc123');
    client.get('/api/tickets').subscribe();
    const req = http.expectOne('/api/tickets');
    expect(req.request.headers.get('Authorization')).toBe('Bearer abc123');
    req.flush([]);
  });

  it('does not add the header when there is no token', () => {
    client.get('/api/tickets').subscribe();
    const req = http.expectOne('/api/tickets');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush([]);
  });

  it('logs out when an authenticated request returns 401', () => {
    const logout = vi.spyOn(auth, 'logout').mockImplementation(() => {});
    auth.token.set('expired');
    client.get('/api/tickets').subscribe({ error: () => {} });
    http.expectOne('/api/tickets').flush({}, { status: 401, statusText: 'Unauthorized' });
    expect(logout).toHaveBeenCalled();
  });

  it('does not log out on 401 when there was no token (e.g. wrong password)', () => {
    const logout = vi.spyOn(auth, 'logout').mockImplementation(() => {});
    client.post('/api/auth/login', {}).subscribe({ error: () => {} });
    http.expectOne('/api/auth/login').flush({}, { status: 401, statusText: 'Unauthorized' });
    expect(logout).not.toHaveBeenCalled();
  });

  it('does not log out on 403 (authorization, not authentication)', () => {
    const logout = vi.spyOn(auth, 'logout').mockImplementation(() => {});
    auth.token.set('abc');
    client.get('/api/users').subscribe({ error: () => {} });
    http.expectOne('/api/users').flush({}, { status: 403, statusText: 'Forbidden' });
    expect(logout).not.toHaveBeenCalled();
  });
});
