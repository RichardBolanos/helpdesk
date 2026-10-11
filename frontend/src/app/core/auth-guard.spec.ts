import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  Router,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { AuthService } from './auth.service';
import { authGuard } from './auth-guard';

describe('authGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) =>
    TestBed.runInInjectionContext(() => authGuard(...guardParameters));
  const run = () =>
    executeGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot);

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideRouter([])] });
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });

  it('allows access when the user is logged in', () => {
    const auth = TestBed.inject(AuthService);
    auth.token.set('abc');
    auth.user.set({ id: 1, name: 'Ana', email: 'a@x.com', role: 'user', is_active: true });
    expect(run()).toBe(true);
  });

  it('redirects to /login when there is no session', () => {
    const result = run() as UrlTree;
    expect(TestBed.inject(Router).serializeUrl(result)).toBe('/login');
  });
});
