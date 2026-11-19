import { test, expect, Page } from '@playwright/test';

const headers = { 'X-Prototipo-Client': 'web' };
const unique = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;

async function login(page: Page, role: 'profesor' | 'estudiante') {
  await page.goto('/login');
  await page.getByRole('link', { name: `Entrar como ${role}`, exact: true }).click();
  await expect(page).toHaveURL(/\/inicio$/);
}

async function finishPractice(page: Page) {
  for (let index = 0; index < 3; index++) {
    await page.getByRole('radio').first().check();
    await page.getByRole('button', { name: 'Comprobar respuesta', exact: true }).click();
    await page.getByRole('button', { name: index === 2 ? 'Ver mi resultado' : 'Siguiente pregunta', exact: true }).click();
  }
  await expect(page.locator('#result-title')).toBeVisible();
}

async function fieldError(page: Page, selector: string) {
  const field = page.locator(selector);
  await expect(field).toHaveAttribute('aria-invalid', 'true');
  const ids = (await field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
  expect(ids.length).toBeGreaterThan(0);
  const descriptions = await Promise.all(ids.map(id => page.locator(`[id="${id}"]`).innerText()));
  return descriptions.join(' ');
}

test('UX-01/04/05: corrige el perfil, lo carga al entrar y lo aplica a una preparación real', async ({ page }, info) => {
  test.setTimeout(300_000);
  await login(page, 'profesor');
  const run = unique();
  const course = `QA perfiles ${run}`;
  const title = `Fuente de derivadas ${run}`;
  const upload = await page.request.post('/api/v1/documents/upload', {
    headers,
    multipart: {
      title, course, source_reference: 'Material sintético de QA', permission_note: 'Autorizado para pruebas locales',
      authorization_confirmed: 'true',
      file: {
        name: `derivadas-${run}.txt`, mimeType: 'text/plain',
        buffer: Buffer.from('La derivada mide la tasa de cambio instantánea. Para f(x)=x^2, la derivada es 2x. La regla de la potencia indica que la derivada de x^n es n*x^(n-1). Un ejemplo: en x=3, la pendiente de x^2 es 6. Primero se identifica el exponente y después se aplica la regla de derivación.'),
      },
    },
  });
  expect(upload.status(), await upload.text()).toBe(201);
  const document = await upload.json();
  try {
    for (const operation of ['process', 'index', 'publish']) {
      const response = await page.request.post(`/api/v1/documents/${document.id}/${operation}`, { headers, timeout: 180_000 });
      expect(response.status(), await response.text()).toBe(200);
    }
    await page.goto('/perfiles');
    await page.locator('#studentId').fill('ALUMNO 1');
    await page.locator('#profileTopic').fill('Derivadas');
    await page.locator('#performance').fill('101');
    await page.locator('#attempts').fill('3');
    await page.getByRole('checkbox', { name: /Confirmo que son datos ficticios/ }).check();
    await page.getByRole('button', { name: /Guardar perfil/ }).click();
    expect(await fieldError(page, '#studentId')).toMatch(/espacios|letras|identificador/i);
    expect(await fieldError(page, '#performance')).toMatch(/0.*100|100/);
    await page.screenshot({ path: info.outputPath('validacion-campos.png') });
    await page.locator('#studentId').fill(`QA-${run}`);
    await page.locator('#performance').fill('35');
    await page.locator('#frequentErrors').fill('regla_potencia\nregla_potencia');
    await page.getByRole('button', { name: /Guardar perfil/ }).click();
    expect(await fieldError(page, '#frequentErrors')).toMatch(/repetid|duplicad|diferentes/i);
    await page.screenshot({ path: info.outputPath('validacion-duplicados.png') });
    await page.locator('#frequentErrors').fill('regla_potencia');
    const created = page.waitForResponse(r => r.url().endsWith('/api/v1/profiles') && r.request().method() === 'POST');
    await page.getByRole('button', { name: /Guardar perfil/ }).click();
    const profileResponse = await created;
    expect(profileResponse.status(), await profileResponse.text()).toBe(201);
    const profile = await profileResponse.json();
    await page.reload();
    await expect(page.getByRole('button', { name: `Abrir perfil QA-${run}`, exact: true })).toBeVisible();
    await page.screenshot({ path: info.outputPath('perfiles-carga-automatica.png') });
    await page.getByRole('button', { name: `Abrir perfil QA-${run}`, exact: true }).click();
    await page.getByRole('link', { name: 'Usar este perfil', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`profile_id=${profile.id}`));
    await page.locator('#resource-course').fill(course);
    await page.locator('.ng-option').filter({ hasText: new RegExp(course, 'i') }).click();
    await page.getByRole('button', { name: /Continuar: definir recurso/ }).click();
    await expect(page.locator('#difficulty')).toBeDisabled();
    await expect(page.locator('#topic')).toHaveAttribute('readonly', '');
    await expect(page.locator('#topic')).toHaveValue('Derivadas');
    await page.getByRole('button', { name: 'Quitar perfil', exact: true }).click();
    await expect(page.locator('#difficulty')).toBeEnabled();
    await expect(page.locator('#topic')).not.toHaveAttribute('readonly', '');
    await page.locator('#difficulty').selectOption('advanced');
    await page.getByRole('button', { name: 'Elegir perfil de aprendizaje', exact: true }).click();
    await page.locator('#resource-profile').selectOption(profile.id);
    await expect(page.locator('#difficulty')).toBeDisabled();
    await page.locator('.profile-options').screenshot({ path: info.outputPath('perfil-selector.png'), animations: 'disabled' });
    await page.locator('#objective').fill('Comprender la derivada como tasa de cambio con un ejemplo guiado.');
    const preparation = page.waitForResponse(r => r.url().endsWith('/api/v1/content/prepare'), { timeout: 180_000 });
    await page.getByRole('button', { name: /Continuar: buscar fuentes/ }).click();
    const response = await preparation;
    expect(response.status(), await response.text()).toBe(201);
    const prepared = await response.json();
    expect(prepared.adaptation.profile.id).toBe(profile.id);
    expect(prepared.adaptation.effective_difficulty).toBe('basic');
    expect(prepared.sources.every((source: { document_id: string }) => source.document_id === document.id)).toBeTruthy();
    await expect(page.getByText('Adaptación revisable', { exact: true })).toBeVisible();
    await page.screenshot({ path: info.outputPath('perfil-aplicado.png'), fullPage: true });
    await info.attach('perfil-preparacion', { body: Buffer.from(JSON.stringify({ profile, prepared }, null, 2)), contentType: 'application/json' });
    await page.goto('/documentos');
    const row = page.locator('.document-row').filter({ hasText: title });
    await expect(row).toContainText('Habilitado');
    await row.scrollIntoViewIfNeeded();
    await page.screenshot({ path: info.outputPath('estados-habilitado.png') });
    const withdrawn = await page.request.post(`/api/v1/documents/${document.id}/withdraw`, { headers });
    expect(withdrawn.status()).toBe(200);
    await page.getByRole('button', { name: 'Actualizar', exact: true }).click();
    await expect(row).toContainText('Sin habilitar');
    await row.scrollIntoViewIfNeeded();
    await page.screenshot({ path: info.outputPath('estados-sin-habilitar.png') });
  } finally {
    await page.request.post(`/api/v1/documents/${document.id}/withdraw`, { headers });
  }
});

test('UX-03: cancelar reinicio, salida, logout y recarga conserva el resultado; guardar continúa una sola vez', async ({ page }, info) => {
  await login(page, 'estudiante');
  await page.goto('/practica');
  await finishPractice(page);
  const resultText = await page.locator('#result-title').innerText();
  for (const name of ['Volver a practicar', 'Cerrar sesión']) {
    await page.getByRole('button', { name, exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'Resultado sin guardar', exact: true });
    await expect(dialog).toBeVisible();
    if (name === 'Volver a practicar') await page.screenshot({ path: info.outputPath('resultado-confirmacion.png') });
    await dialog.getByRole('button', { name: 'Seguir aquí', exact: true }).click();
    await expect(page.locator('#result-title')).toHaveText(resultText);
    expect((await page.request.get('/api/v1/auth/me')).status()).toBe(200);
  }
  const beforeUnload = page.waitForEvent('dialog');
  const reload = page.reload().catch(() => null);
  const nativeDialog = await beforeUnload;
  expect(nativeDialog.type()).toBe('beforeunload');
  await nativeDialog.dismiss();
  await reload;
  await expect(page.locator('#result-title')).toHaveText(resultText);
  await page.getByRole('link', { name: '← Volver al inicio', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Resultado sin guardar', exact: true });
  await dialog.getByRole('button', { name: 'Seguir aquí', exact: true }).click();
  await expect(page).toHaveURL(/\/practica$/);
  await page.getByRole('link', { name: '← Volver al inicio', exact: true }).click();
  let saves = 0;
  page.on('request', request => {
    if (request.method() === 'POST' && /\/practice\/attempts$/.test(request.url())) saves++;
  });
  await dialog.getByRole('button', { name: 'Guardar y continuar', exact: true }).click();
  await expect(page).toHaveURL(/\/inicio$/);
  expect(saves).toBe(1);
  await page.goto('/practica#history-title');
  await expect(page.locator('#history-title')).toBeVisible();
  await page.screenshot({ path: info.outputPath('resultado-protegido-guardado.png'), fullPage: true });
});

test('UX-03: el descarte explícito permite reiniciar sin guardar', async ({ page }) => {
  await login(page, 'estudiante');
  await page.goto('/practica');
  await finishPractice(page);
  await page.getByRole('button', { name: 'Volver a practicar', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Resultado sin guardar', exact: true });
  await dialog.getByRole('button', { name: 'Descartar y continuar', exact: true }).click();
  await expect(page.locator('#result-title')).not.toBeVisible();
  await expect(page.getByText('Pregunta 1 de 3', { exact: true })).toBeVisible();
});

test('A11Y-02: el teclado mantiene una ubicación visible al cambiar de pregunta', async ({ page }, info) => {
  await login(page, 'estudiante');
  await page.goto('/practica');
  await page.getByRole('radio').first().check();
  const check = page.getByRole('button', { name: 'Comprobar respuesta', exact: true });
  await check.focus();
  await page.keyboard.press('Enter');
  const next = page.getByRole('button', { name: 'Siguiente pregunta', exact: true });
  await next.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('#question-title')).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('radio').first()).toBeFocused();
  await page.screenshot({ path: info.outputPath('foco-pregunta.png'), fullPage: true });
  // Discard checked work before ending the context when a pending-work guard exists.
});

test('VIS-01/03: texto literal claro y título enfocado totalmente visible en cuatro tamaños', async ({ page }, info) => {
  await login(page, 'profesor');
  await page.goto('/documentos');
  await expect(page.locator('.search-hint')).toContainText('coincidencias de texto, sin distinguir mayúsculas');
  await expect(page.locator('.search-hint a')).toHaveAttribute('href', '/busqueda');
  await page.screenshot({ path: info.outputPath('busqueda-literal.png') });
  for (const width of [320, 390, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await page.getByRole('button', { name: 'Actualizar', exact: true }).click();
    await expect(page.locator('#library-title')).toBeFocused();
    await expect.poll(() => page.evaluate(() => {
      const target = document.getElementById('library-title')!.getBoundingClientRect();
      const header = document.querySelector('.site-header')!.getBoundingClientRect();
      return target.top >= header.bottom && target.bottom <= window.innerHeight;
    })).toBeTruthy();
    await page.screenshot({ path: info.outputPath(`foco-biblioteca-${width}.png`) });
  }
  await page.setViewportSize({ width: 390, height: 900 });
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await page.getByRole('button', { name: 'Actualizar', exact: true }).click();
  await expect.poll(() => page.evaluate(() => {
    const target = document.getElementById('library-title')!.getBoundingClientRect();
    return target.top >= document.querySelector('.site-header')!.getBoundingClientRect().bottom;
  })).toBeTruthy();
  await page.screenshot({ path: info.outputPath('foco-biblioteca-texto-200.png') });
});

test('A11Y-01: instrucciones y etiquetas alcanzan contraste de texto normal', async ({ page }, info) => {
  async function contrast(selector: string) {
    return page.locator(selector).evaluate(element => {
      const rgb = (color: string) => color.match(/[\d.]+/g)!.slice(0, 3).map(Number);
      const luminance = (color: number[]) => color.map(value => value / 255).map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
      let current: Element | null = element;
      let background = 'rgb(255,255,255)';
      while (current) {
        const color = getComputedStyle(current).backgroundColor;
        if (color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') { background = color; break; }
        current = current.parentElement;
      }
      const foreground = getComputedStyle(element).color;
      const first = luminance(rgb(foreground)), second = luminance(rgb(background));
      return { foreground, background, ratio: (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05) };
    });
  }
  await page.goto('/login');
  await expect(page.getByRole('link', { name: 'Entrar como estudiante' })).toBeVisible();
  const badge = await contrast('.role-pill:not(.docencia-pill)');
  expect(badge.ratio).toBeGreaterThanOrEqual(4.5);
  await page.getByRole('link', { name: 'Entrar como estudiante', exact: true }).click();
  await page.goto('/practica');
  const legend = await contrast('fieldset legend');
  expect(legend.ratio).toBeGreaterThanOrEqual(4.5);
  await info.attach('contrastes', { body: Buffer.from(JSON.stringify({ badge, legend }, null, 2)), contentType: 'application/json' });
  await page.locator('fieldset legend').scrollIntoViewIfNeeded();
  await page.screenshot({ path: info.outputPath('contraste-corregido.png') });
});
