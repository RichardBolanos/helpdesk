import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/auth.service';
import { User } from '../../core/models';
import { Users } from './users';

const admin: User = { id: 1, name: 'Admin', email: 'admin@helpdesk.com', role: 'admin', is_active: true };
const luis: User = { id: 3, name: 'Luis', email: 'luis@example.com', role: 'user', is_active: true };
const url = `${environment.apiUrl}/users`;

describe('Users', () => {
  let component: Users;
  let fixture: ComponentFixture<Users>;
  let http: HttpTestingController;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Users],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    http = TestBed.inject(HttpTestingController);
    TestBed.inject(AuthService).user.set(admin);
    fixture = TestBed.createComponent(Users);
    component = fixture.componentInstance;
    http.expectOne(url).flush([admin, luis]);
    await fixture.whenStable();
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('lists every user', () => {
    const rows = (fixture.nativeElement as HTMLElement).querySelectorAll('tbody tr');
    expect(rows.length).toBe(2);
    expect(rows[1].textContent).toContain('luis@example.com');
  });

  it('isMe() identifies the logged-in user', () => {
    expect(component.isMe(admin)).toBe(true);
    expect(component.isMe(luis)).toBe(false);
  });

  it('disables the controls of the admin\'s own row', () => {
    const rows = (fixture.nativeElement as HTMLElement).querySelectorAll('tbody tr');
    expect(rows[0].querySelector('input')?.disabled).toBe(true);
    expect(rows[1].querySelector('input')?.disabled).toBe(false);
  });

  it('update() sends a PATCH with the new role and refreshes the row', () => {
    component.update(luis, { role: 'agent' });
    const req = http.expectOne(`${url}/3`);
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ role: 'agent' });
    req.flush({ ...luis, role: 'agent' });
    expect(component.users().find((u) => u.id === 3)?.role).toBe('agent');
  });

  it('update() reloads the list and shows an error on failure', () => {
    component.update(luis, { is_active: false });
    http.expectOne(`${url}/3`).flush({}, { status: 400, statusText: 'Bad Request' });
    expect(component.error()).toBe('No se pudo actualizar el usuario');
    http.expectOne(url).flush([admin, luis]);
  });
});
