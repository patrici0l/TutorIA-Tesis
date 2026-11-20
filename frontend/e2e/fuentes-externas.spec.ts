import { test, expect } from '@playwright/test';

test('Wikipedia real: revisión, importación privada, índice, RAG y retirada', async ({ page }, info) => {
  test.skip(process.env.WIKIPEDIA_LIVE_TEST !== '1', 'Prueba optativa: consulta Wikipedia y crea material de prueba.');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const headers = { 'X-Prototipo-Client': 'web' };
  const course = 'SYN-WIKIPEDIA-' + Date.now();
  let identifier: string | undefined;
  try {
    await page.goto('/login');
    await page.getByRole('link', { name: 'Entrar como profesor', exact: true }).click();
    await expect(page).toHaveURL(/\/inicio$/);
    await page.goto('/documentos');
    await page.getByRole('link', { name: 'Buscar fuentes externas', exact: true }).click();
    await page.getByLabel('Tema que quieres buscar').fill('Derivada');
    await page.getByRole('button', { name: 'Buscar en Wikipedia', exact: true }).click();
    const item = page.locator('.results li').filter({ has: page.getByText('Derivada', { exact: true }) });
    await item.getByRole('button', { name: 'Revisar artículo' }).click();
    await expect(page.locator('#external-preview')).toHaveText('Derivada');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: info.outputPath('wikipedia-desktop.png'), fullPage: true });
    await page.getByLabel('Asignatura', { exact: true }).fill(course);
    await page.getByRole('checkbox').check();
    const imported = page.waitForResponse(r => r.url().endsWith('/wikipedia/import') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Añadir a mis documentos' }).click();
    const response = await imported;
    expect(response.status(), await response.text()).toBe(201);
    const document = await response.json();
    identifier = document.id;
    expect(document.published_at).toBeNull();
    expect(document.external_source.provider).toBe('wikipedia_es');
    await expect(page.locator('#external-success')).toContainText('Material añadido');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: info.outputPath('wikipedia-mobile.png'), fullPage: true });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const snapshot = await page.request.get('/api/v1/documents/external/wikipedia/snapshot/' + identifier);
    expect(snapshot.status()).toBe(200);
    const raw = await snapshot.json();
    expect(raw.article.parse.revid).toBe(document.external_source.revision_id);
    expect(raw.article.parse.wikitext.length).toBeGreaterThan(80);
    const processed = await page.request.post(`/api/v1/documents/${identifier}/process`, { headers });
    expect(processed.status(), await processed.text()).toBe(200);
    expect((await processed.json()).chunk_count).toBeGreaterThan(0);
    const indexed = await page.request.post(`/api/v1/documents/${identifier}/index`, { headers, timeout: 180000 });
    expect(indexed.status(), await indexed.text()).toBe(200);
    const search = () => page.request.post('/api/v1/rag/search', { headers,
      data: { course, query: 'derivada y tasa de cambio', top_k: 2 } });
    expect((await (await search()).json()).results).toEqual([]);
    expect((await page.request.post(`/api/v1/documents/${identifier}/publish`, { headers })).status()).toBe(200);
    const found = await search();
    expect(found.status(), await found.text()).toBe(200);
    const results = (await found.json()).results;
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].external_source.revision_id).toBe(document.external_source.revision_id);
    expect(results[0].source_reference).toContain('oldid=');
    const prepared = await page.request.post('/api/v1/content/prepare', { headers, data: {
      course, topic: 'Derivada', learning_objective: 'Explicar la tasa de cambio instantánea',
      resource_type: 'EXPLANATION', difficulty: 'basic',
    } });
    expect(prepared.status(), await prepared.text()).toBe(201);
    expect((await prepared.json()).sources[0].external_source.provider).toBe('wikipedia_es');
    expect((await page.request.post(`/api/v1/documents/${identifier}/withdraw`, { headers })).status()).toBe(200);
    expect((await (await search()).json()).results).toEqual([]);
  } finally {
    if (identifier) {
      await page.request.post(`/api/v1/documents/${identifier}/withdraw`, { headers });
      await page.request.delete(`/api/v1/documents/${identifier}`, { headers });
    }
  }
});
