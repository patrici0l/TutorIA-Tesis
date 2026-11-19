import { test, expect, Page } from '@playwright/test';

// All requests reach the real application, database and pinned embedding model.
// Only synthetic, uniquely named documents and profiles are created.
const run = process.env.E2E_RUN_ID || Date.now().toString(36);
const headers = { 'X-Prototipo-Client': 'web' };

async function login(page: Page, role: 'profesor' | 'estudiante') {
  await page.goto('/login');
  await page.getByRole('link', { name: `Entrar como ${role}` }).click();
  await expect(page).toHaveURL(/\/inicio$/);
}

test('sin sesión: protege navegación y API privada', async ({ page, request }) => {
  await page.goto('/documentos');
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole('heading', { name: 'Ingreso a la plataforma' })).toBeVisible();
  expect((await request.get('/api/v1/documents')).status()).toBe(401);
});

test('profesor: registra perfil sintético y conserva sus datos al recargar', async ({ page }) => {
  await login(page, 'profesor');
  await page.goto('/perfiles');
  await page.locator('#studentId').fill(`SYN-E2E-${run}`);
  await page.locator('#profileTopic').fill('Derivadas');
  await page.locator('#performance').fill('35');
  await page.locator('#attempts').fill('3');
  await page.locator('#mastery').selectOption('low');
  await page.locator('#support').selectOption('reinforcement');
  await page.locator('#frequentErrors').fill('regla_potencia');
  await page.getByRole('checkbox', { name: /Confirmo que son datos ficticios/ }).check();
  await page.getByRole('button', { name: /Guardar perfil/ }).click();
  await expect(page.locator('#profile-detail-title')).toContainText(`SYN-E2E-${run}`);
  await page.reload();
  await expect(page.getByRole('button', { name: `Abrir perfil SYN-E2E-${run}`, exact: true })).toBeVisible();
  await page.getByRole('button', { name: `Abrir perfil SYN-E2E-${run}`, exact: true }).click();
  await expect(page.locator('#profile-detail-title')).toContainText('Derivadas');
  await expect(page.locator('.detail')).toContainText('regla_potencia');
});

test('profesor: requiere metadatos y rechaza archivo no admitido', async ({ page }) => {
  await login(page, 'profesor');
  await page.goto('/documentos');
  await page.getByRole('button', { name: '+ Subir documento', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Guardar documento', exact: true })).toBeDisabled();
  await page.locator('#document-file').setInputFiles({
    name: 'no-admitido.exe', mimeType: 'application/octet-stream', buffer: Buffer.from('E2E'),
  });
  await expect(page.locator('#document-panel-error')).toContainText('no es válido');
  await expect(page.getByRole('button', { name: 'Guardar documento', exact: true })).toBeDisabled();
});

const subjects = [
  {
    label: 'Calculo', topic: 'Derivada y tasa de cambio', query: '¿Qué representa la derivada?',
    text: 'La derivada representa la tasa de cambio instantánea de una función. Para f(x)=x^2, la derivada es f\'(x)=2x. La regla de la potencia indica que la derivada de x^n es n*x^(n-1). La pendiente de la recta tangente coincide con el valor de la derivada. Por ejemplo en x=3 la pendiente de x^2 es 6.',
  },
  {
    label: 'Redes', topic: 'Direccionamiento IPv4', query: '¿Qué es una dirección IPv4?',
    text: 'Una dirección IPv4 identifica una interfaz de red mediante 32 bits organizados en cuatro octetos. Una máscara de subred separa la parte de red y la parte de host. La dirección 192.168.10.5 con máscara 255.255.255.0 pertenece a la red 192.168.10.0/24. Una puerta de enlace permite comunicarse con otras redes. Los paquetes IP se encaminan según su dirección de destino.',
  },
];

for (const subject of subjects) {
  test(`docente E2E ${subject.label}: carga → índice real → publicación → RAG → preparación → retirada`, async ({ page }, info) => {
    await login(page, 'profesor');
    const course = `E2E ${subject.label} ${run}`;
    const title = `Material ${subject.label} ${run}`;
    await page.goto('/documentos');
    await page.getByRole('button', { name: '+ Subir documento', exact: true }).click();
    await page.locator('#document-title').fill(title);
    await page.locator('#document-course').fill(course);
    await page.locator('#document-source').fill('Texto sintético creado para verificación técnica E2E');
    await page.locator('#document-permission').fill('Autorizado para pruebas locales; sin datos personales');
    await page.locator('#document-authorized').check();
    await page.locator('#document-auto-enable').check();
    await page.locator('#document-file').setInputFiles({
      name: `${subject.label}-${run}.txt`, mimeType: 'text/plain', buffer: Buffer.from(subject.text),
    });
    const uploadResponse = page.waitForResponse(r => r.url().endsWith('/api/v1/documents/upload') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Guardar documento', exact: true }).click();
    const upload = await uploadResponse;
    expect(upload.status(), await upload.text()).toBe(201);
    const document = await upload.json();
    const dialog = page.getByRole('dialog');
    const publish = dialog.getByRole('button', { name: 'Habilitar como fuente', exact: true });
    await expect(publish).toBeEnabled({ timeout: 180_000 });
    // Indexing alone must not publish documents.
    const before = await page.request.post('/api/v1/rag/search', {
      headers, data: { course, query: subject.query, min_similarity: 0, top_k: 3 },
    });
    expect(before.status()).toBe(200);
    expect((await before.json()).results).toEqual([]);
    await publish.click();
    await expect(dialog.getByRole('button', { name: 'Retirar de recursos', exact: true })).toBeVisible();
    await dialog.getByRole('button', { name: 'Cerrar', exact: true }).click();

    await page.goto('/busqueda');
    await page.locator('#source-course').fill(course);
    await page.locator('#source-query').fill(subject.query);
    await page.locator('#min-similarity').fill('0');
    const searchResponse = page.waitForResponse(r => r.url().endsWith('/api/v1/rag/search'), { timeout: 180_000 });
    await page.getByRole('button', { name: /Buscar fuentes/ }).click();
    const search = await searchResponse;
    expect(search.status(), await search.text()).toBe(200);
    const hits = (await search.json()).results;
    expect(hits.length).toBeGreaterThan(0);
    expect(hits.every((h: any) => h.document_id === document.id)).toBeTruthy();
    await expect(page.locator('.source').first()).toContainText(title);
    const original = await page.request.get(`/api/v1/documents/${document.id}/original`);
    expect(original.status()).toBe(200);
    expect((await original.body()).toString()).toBe(subject.text);
    await page.screenshot({ path: info.outputPath('fuentes.png'), fullPage: true });
    // A different course must not retrieve this document.
    const isolated = await page.request.post('/api/v1/rag/search', {
      headers, data: { course: `Sin fuentes ${run}`, query: subject.query, min_similarity: 0 },
    });
    expect(isolated.status()).toBe(200);
    expect((await isolated.json()).results).toEqual([]);

    await page.goto(`/recursos?course=${encodeURIComponent(course)}`);
    await page.getByRole('button', { name: /Continuar: definir recurso/ }).click();
    await page.locator('#topic').fill(subject.topic);
    await page.locator('#objective').fill(`Comprender ${subject.topic.toLowerCase()} con un ejemplo resuelto.`);
    const prepareResponse = page.waitForResponse(r => r.url().endsWith('/api/v1/content/prepare'), { timeout: 180_000 });
    await page.getByRole('button', { name: /Continuar: buscar fuentes/ }).click();
    const preparedResponse = await prepareResponse;
    expect(preparedResponse.status(), await preparedResponse.text()).toBe(201);
    const prepared = await preparedResponse.json();
    expect(prepared.sources.length).toBeGreaterThan(0);
    expect(prepared.sources.every((s: any) => s.document_id === document.id)).toBeTruthy();
    await expect(page.locator('#sources-title')).toContainText(subject.topic);
    await page.screenshot({ path: info.outputPath('preparacion.png'), fullPage: true });

    const quota = await (await page.request.get('/api/v1/content/quota')).json();
    if (!quota.enabled) {
      await expect(page.locator('#generate-resource')).toBeDisabled();
      await expect(page.locator('#generate-resource')).toBeVisible();
      await expect(page.locator('#generation-availability')).toContainText(/habilitada|disponible|generación/i);
      await page.locator('#generate-resource').scrollIntoViewIfNeeded();
      const buttonAppearance = await page.locator('#generate-resource').evaluate(element => {
        const style = getComputedStyle(element);
        return { text: element.textContent, opacity: style.opacity, background: style.backgroundColor, color: style.color, visibility: style.visibility, bounds: element.getBoundingClientRect().toJSON() };
      });
      await info.attach('boton-generacion', { body: Buffer.from(JSON.stringify(buttonAppearance, null, 2)), contentType: 'application/json' });
      await page.locator('#generate-resource').screenshot({ path: info.outputPath('generacion-boton.png'), animations: 'disabled' });
      await page.screenshot({ path: info.outputPath('generacion-bloqueada.png') });
      // The UI prevents the action; the API must still reject a direct request without using quota.
      const generation = await page.request.post(`/api/v1/content/${prepared.id}/generate`, { headers, data: {} });
      expect(generation.status()).toBe(503);
      const quotaAfter = await (await page.request.get('/api/v1/content/quota')).json();
      expect(quotaAfter.used).toBe(quota.used);
    } else {
      info.annotations.push({ type: 'scope', description: 'Generación externa no enviada por esta prueba sintética.' });
    }

    await page.goto('/documentos');
    await page.getByRole('button', { name: `Ver detalles de ${title}`, exact: true }).click();
    await page.getByRole('dialog').getByRole('button', { name: 'Retirar de recursos', exact: true }).click();
    await expect(page.getByRole('dialog').getByRole('button', { name: 'Habilitar como fuente', exact: true })).toBeVisible();
    const after = await page.request.post('/api/v1/rag/search', {
      headers, data: { course, query: subject.query, min_similarity: 0 },
    });
    expect(after.status()).toBe(200);
    expect((await after.json()).results).toEqual([]);
    expect((await page.request.get(`/api/v1/documents/${document.id}/original`)).status()).toBe(200);
    // The saved preparation remains visible with its original sources.
    const history = await page.request.get(`/api/v1/content/history/${prepared.id}`);
    expect(history.status()).toBe(200);
    await info.attach('trazabilidad', { body: Buffer.from(JSON.stringify({ document, prepared, hits }, null, 2)), contentType: 'application/json' });
  });
}

test('estudiante: completa práctica, guarda y consulta intento persistente', async ({ page }, info) => {
  await login(page, 'estudiante');
  await page.goto('/practica');
  await expect(page.getByRole('button', { name: 'Comprobar respuesta', exact: true })).toBeDisabled();
  await page.getByRole('button', { name: 'Ver una pista', exact: true }).click();
  await expect(page.locator('#practice-hint')).toBeVisible();
  for (let i = 0; i < 3; i++) {
    await page.getByRole('radio').first().check();
    await page.getByRole('button', { name: 'Comprobar respuesta', exact: true }).click();
    await expect(page.locator('.feedback')).toBeVisible();
    await page.getByRole('button', { name: i === 2 ? 'Ver mi resultado' : 'Siguiente pregunta', exact: true }).click();
  }
  await expect(page.locator('#result-title')).toContainText('de 3 respuestas correctas');
  await page.getByRole('button', { name: 'Guardar resultado', exact: true }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Resultado guardado' })).toBeVisible();
  await page.reload();
  await page.getByRole('button', { name: 'Mi historial', exact: true }).click();
  await expect(page.locator('#history-title')).toBeVisible();
  await page.getByRole('button', { name: /Revisar intento/ }).first().click();
  await expect(page.locator('#review-title')).toHaveText('Revisa tus respuestas');
  await page.screenshot({ path: info.outputPath('historial-estudiante.png'), fullPage: true });
});

test('estudiante: bloquea operaciones y datos privados del docente', async ({ page }) => {
  await login(page, 'estudiante');
  for (const route of ['/documentos', '/perfiles', '/busqueda', '/recursos']) {
    await page.goto(route);
    await expect(page.getByRole('heading', { name: 'Espacio docente', exact: true })).toBeVisible();
  }
  for (const path of ['/api/v1/documents', '/api/v1/profiles', '/api/v1/content/history']) {
    expect((await page.request.get(path)).status(), path).toBe(403);
  }
  const response = await page.request.post('/api/v1/rag/search', {
    headers, data: { course: 'E2E', query: 'derivada' },
  });
  expect(response.status()).toBe(403);
});

test('sesión: cerrar acceso impide reutilizar la sesión', async ({ page }) => {
  await login(page, 'profesor');
  const logout = await page.request.post('/api/v1/auth/logout', { headers, data: {} });
  expect(logout.ok()).toBeTruthy();
  expect((await page.request.get('/api/v1/auth/me')).status()).toBe(401);
  await page.goto('/recursos');
  await expect(page).toHaveURL(/\/login$/);
});

test('móvil: acceso y práctica sin desbordamiento horizontal', async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, 'estudiante');
  await page.goto('/practica');
  await expect(page.locator('#question-title')).toBeVisible();
  for (const width of [320, 390, 680]) {
    await page.setViewportSize({ width, height: 844 });
    await page.screenshot({ path: info.outputPath(`movil-${width}.png`), fullPage: true });
    const dimensions = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
      overflowing: [...document.querySelectorAll('body *')].map(element => ({
        tag: element.tagName, class: element.className,
        right: Math.round(element.getBoundingClientRect().right),
        left: Math.round(element.getBoundingClientRect().left),
      })).filter(element => element.right > window.innerWidth + 1 || element.left < -1).slice(0, 30),
    }));
    await info.attach(`dimensiones-movil-${width}`, { body: Buffer.from(JSON.stringify(dimensions, null, 2)), contentType: 'application/json' });
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth), { timeout: 5000 }).toBeLessThanOrEqual(width);
    await expect(page.getByRole('button', { name: 'Cerrar sesión', exact: true })).toBeInViewport({ ratio: 1 });
  }
  await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
    await expect(page.getByRole('button', { name: 'Cerrar sesión', exact: true })).toBeInViewport({ ratio: 1 });
    await page.screenshot({ path: info.outputPath(`movil-${width}-texto-200.png`), animations: 'disabled' });
  }
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click();
  await expect(page).toHaveURL(/\/login$/);
});

test('menú real: abre, cierra con Escape y navega con foco restaurado', async ({ page }) => {
  await login(page, 'profesor');
  const trigger = page.getByRole('button', { name: 'Explorar', exact: true });
  await trigger.click();
  const menu = page.getByRole('dialog', { name: 'Explorar', exact: true });
  await expect(menu).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(menu).not.toBeVisible();
  await expect(trigger).toBeFocused();
  await trigger.click();
  await menu.getByRole('link', { name: /^Mis documentos/ }).click();
  await expect(page).toHaveURL(/\/documentos$/);
  await expect(menu).not.toBeVisible();
});
