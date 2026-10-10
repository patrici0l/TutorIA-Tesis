import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ProfilePage, ProfileRequest, ProfileResponse } from '../modelos/profile.model';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private readonly http = inject(HttpClient);
  create(request: ProfileRequest) {
    return this.http.post<ProfileResponse>('/api/v1/profiles', request);
  }
  page(offset = 0) {
    return this.http.get<ProfilePage>('/api/v1/profiles', { params: { offset, limit: 10 } });
  }
  detail(id: string) {
    return this.http.get<ProfileResponse>(`/api/v1/profiles/${id}`);
  }
}
