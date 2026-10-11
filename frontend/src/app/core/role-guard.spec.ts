import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  RouterStateSnapshot,
  UrlTree,
  provideRouter,
} from '@angular/router';
import { AuthService } from './auth.service';
import { Role } from './models';
import { roleGuard } from './role-guard';

describe('roleGuard', () => {
  const run = (...roles: Role[]) =>
    TestBed.runInInjectionContext(() =>
      roleGuard(...roles)({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot),
    );

  function loginAs(role: Role) {
    const auth = TestBed.inject(AuthService);
    auth.token.set('abc');
    auth.user.set({ id: 1, name: 'Ana', email: 'a@x.com', role, is_active: true });
  }

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideRouter([])] });
  });

  it('allows a user with one of the required roles', () => {
    loginAs('admin');
    expect(run('admin')).toBe(true);
  });

  it('redirects a user without the required role to /tickets', () => {
    loginAs('user');
    const result = run('admin') as UrlTree;
    expect(TestBed.inject(Router).serializeUrl(result)).toBe('/tickets');
  });

  it('redirects to /login when there is no session', () => {
    const result = run('admin') as UrlTree;
    expect(TestBed.inject(Router).serializeUrl(result)).toBe('/login');
  });

  it('accepts any of several roles', () => {
    loginAs('agent');
    expect(run('agent', 'admin')).toBe(true);
  });
});
