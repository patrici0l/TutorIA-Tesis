import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../../nucleo/servicios/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  readonly auth = inject(AuthService);
  readonly denied = inject(ActivatedRoute).snapshot.queryParamMap.has('error');
}
