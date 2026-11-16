// Registra las dependencias globales de navegación y HTTP.
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withInMemoryScrolling } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './inicio/sesion.interceptor';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(
      routes,
      withInMemoryScrolling({ scrollPositionRestoration: 'enabled', anchorScrolling: 'enabled' }),
    ),
    provideHttpClient(withInterceptors([authInterceptor])),
    providePrimeNG({
      license: 'eyJpZCI6IjA1YmM3ZjNjLWE2ODItNDU5Yi04NzdlLTJjZDJmOTQwZDE2YyIsInByb2R1Y3QiOiJwcmltZXVpIiwidGllciI6ImNvbW11bml0eSIsInR5cGUiOiJkZXYiLCJpYXQiOjE3OTQ4NDI2MTAsImV4cCI6MTgyNjM3ODYxMH0.0lYh9YNZNxOvlP9vju4r8UaZXaeOgaMfY-oveTdaRNMw3xD75uhSGBrStBeLdTjr047AjfxwybUBTcxzvPb5Bg',
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: 'none',
        },
      },
    }),
  ],
};
