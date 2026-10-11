import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../core/auth.service';
import { Role, Ticket } from '../../core/models';
import { Tickets } from './tickets';

const ticket: Ticket = {
  id: 1,
  title: 'La impresora no funciona',
  description: 'Atasco de papel',
  priority: 'high',
  status: 'open',
  created_at: '2026-10-10T15:00:00Z',
  author: { id: 2, name: 'Luis' },
};
const url = `${environment.apiUrl}/tickets`;

describe('Tickets', () => {
  let component: Tickets;
  let fixture: ComponentFixture<Tickets>;
  let http: HttpTestingController;

  /** Crea el componente como un usuario con ese rol y responde a la carga inicial. */
  async function setup(role: Role, tickets: Ticket[] = [ticket]) {
    TestBed.inject(AuthService).user.set({ id: 1, name: 'Ana', email: 'a@x.com', role, is_active: true });
    fixture = TestBed.createComponent(Tickets);
    component = fixture.componentInstance;
    http.expectOne(url).flush(tickets);
    await fixture.whenStable();
    fixture.detectChanges();
  }
  const el = () => fixture.nativeElement as HTMLElement;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [Tickets],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('should create', async () => {
    await setup('user');
    expect(component).toBeTruthy();
  });

  it('lists the tickets returned by the API', async () => {
    await setup('agent');
    expect(el().querySelectorAll('tbody tr').length).toBe(1);
    expect(el().textContent).toContain('La impresora no funciona');
  });

  it('shows an empty message when there are no tickets', async () => {
    await setup('agent', []);
    expect(el().querySelector('tbody')?.textContent).toContain('No hay tickets.');
  });

  describe('as a user', () => {
    beforeEach(() => setup('user'));

    it('sees "Mis tickets" and the creation form', () => {
      expect(el().querySelector('h1')?.textContent).toBe('Mis tickets');
      expect(el().querySelector('form')).toBeTruthy();
    });

    it('cannot change status or delete', () => {
      expect(el().querySelector('tbody select')).toBeNull();
      expect(el().querySelector('button.danger')).toBeNull();
    });

    it('create() posts the ticket, prepends it and clears the form', async () => {
      component.title = 'Nuevo';
      component.description = 'Detalle';
      component.priority = 'low';
      component.create();

      const req = http.expectOne(url);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ title: 'Nuevo', description: 'Detalle', priority: 'low' });
      req.flush({ ...ticket, id: 9, title: 'Nuevo' });

      expect(component.tickets()[0].id).toBe(9);
      expect(component.tickets().length).toBe(2);
      expect(component.title).toBe('');
      expect(component.priority).toBe('medium');
    });
  });

  describe('as an agent', () => {
    beforeEach(() => setup('agent'));

    it('sees "Todos los tickets", a status selector and no creation form or delete button', () => {
      expect(el().querySelector('h1')?.textContent).toBe('Todos los tickets');
      expect(el().querySelector('tbody select')).toBeTruthy();
      expect(el().querySelector('form')).toBeNull();
      expect(el().querySelector('button.danger')).toBeNull();
    });

    it('setStatus() sends a PATCH and updates the row', () => {
      component.setStatus(ticket, 'closed');
      const req = http.expectOne(`${url}/1`);
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual({ status: 'closed' });
      req.flush({ ...ticket, status: 'closed' });
      expect(component.tickets()[0].status).toBe('closed');
    });

    it('setStatus() reloads the list and shows an error when the API fails', () => {
      component.setStatus(ticket, 'closed');
      http.expectOne(`${url}/1`).flush({}, { status: 403, statusText: 'Forbidden' });
      expect(component.error()).toBe('No se pudo actualizar el estado');
      http.expectOne(url).flush([ticket]); // recarga para revertir el cambio visual
    });
  });

  describe('as an admin', () => {
    beforeEach(() => setup('admin'));

    it('sees the delete button', () => {
      expect(el().querySelector('button.danger')).toBeTruthy();
    });

    it('remove() asks for confirmation and deletes the ticket', () => {
      vi.spyOn(window, 'confirm').mockReturnValue(true);
      component.remove(ticket);
      const req = http.expectOne(`${url}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
      expect(component.tickets().length).toBe(0);
    });

    it('remove() does nothing when the confirmation is cancelled', () => {
      vi.spyOn(window, 'confirm').mockReturnValue(false);
      component.remove(ticket);
      http.expectNone(`${url}/1`);
      expect(component.tickets().length).toBe(1);
    });
  });
});
