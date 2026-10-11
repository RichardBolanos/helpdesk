import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { environment } from '../../../environments/environment';
import { Login } from './login';

describe('Login', () => {
  let component: Login;
  let fixture: ComponentFixture<Login>;
  let http: HttpTestingController;
  let router: Router;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    http = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(Login);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders the form with a link to register', () => {
    const el: HTMLElement = fixture.nativeElement;
    expect(el.querySelector('h2')?.textContent).toContain('Iniciar sesión');
    expect(el.querySelectorAll('input').length).toBe(2);
    expect(el.querySelector('a[href="/register"]')).toBeTruthy();
  });

  it('navigates to /tickets after a successful login', () => {
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);
    component.email = 'ana@example.com';
    component.password = 'secret123';
    component.submit();

    const req = http.expectOne(`${environment.apiUrl}/auth/login`);
    expect(req.request.body).toEqual({ email: 'ana@example.com', password: 'secret123' });
    req.flush({
      access_token: 'abc',
      token_type: 'bearer',
      user: { id: 1, name: 'Ana', email: 'ana@example.com', role: 'user', is_active: true },
    });

    expect(navigate).toHaveBeenCalledWith(['/tickets']);
  });

  it('shows "Credenciales incorrectas" on 401 and re-enables the button', async () => {
    component.submit();
    http.expectOne(`${environment.apiUrl}/auth/login`).flush({}, { status: 401, statusText: 'Unauthorized' });
    fixture.detectChanges();

    expect(component.error()).toBe('Credenciales incorrectas');
    expect(component.loading()).toBe(false);
    expect((fixture.nativeElement as HTMLElement).querySelector('.error')?.textContent).toContain(
      'Credenciales incorrectas',
    );
  });

  it('shows a connection error when the server is unreachable', () => {
    component.submit();
    http.expectOne(`${environment.apiUrl}/auth/login`).error(new ProgressEvent('error'));
    expect(component.error()).toBe('No se pudo conectar con el servidor');
  });
});
