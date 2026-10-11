import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../environments/environment';
import { ApiService } from './api.service';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;
  const url = environment.apiUrl;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('tickets() sends GET /tickets', () => {
    service.tickets().subscribe();
    const req = http.expectOne(`${url}/tickets`);
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });

  it('createTicket() sends POST /tickets with the body', () => {
    const data = { title: 'Falla', description: 'No imprime', priority: 'high' as const };
    service.createTicket(data).subscribe();
    const req = http.expectOne(`${url}/tickets`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(data);
    req.flush({});
  });

  it('updateTicketStatus() sends PATCH /tickets/:id with only the status', () => {
    service.updateTicketStatus(7, 'closed').subscribe();
    const req = http.expectOne(`${url}/tickets/7`);
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ status: 'closed' });
    req.flush({});
  });

  it('deleteTicket() sends DELETE /tickets/:id', () => {
    service.deleteTicket(7).subscribe();
    const req = http.expectOne(`${url}/tickets/7`);
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
  });

  it('users() sends GET /users', () => {
    service.users().subscribe();
    const req = http.expectOne(`${url}/users`);
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });

  it('updateUser() sends PATCH /users/:id with the changed fields', () => {
    service.updateUser(3, { role: 'agent' }).subscribe();
    const req = http.expectOne(`${url}/users/3`);
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ role: 'agent' });
    req.flush({});
  });
});
