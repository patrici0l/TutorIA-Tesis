import { test, expect } from '@playwright/test';

test('docente habilita acceso, estudiante prepara con fuentes reales y se respeta la retirada', async ({ page, browser }, info) => {
  test.skip(process.env.STUDENT_LIVE_TEST !== '1', 'Usar un entorno local de prueba con LLM deshabilitado.');
  const headers = { 'X-Prototipo-Client': 'web' };
  const course = 'SYN-ESTUDIANTE-' + Date.now();
  const topic = 'Derivada de una potencia ' + Date.now();
  const studentContext = await browser.newContext();
  const student = await studentContext.newPage();
  let documentId: string | undefined;
  let accessId: string | undefined;
  try {
    await student.goto('/login');
    await student.getByRole('link', { name: 'Entrar como estudiante', exact: true }).click();
    await expect(student).toHaveURL(/\/inicio$/);
    const session = await student.request.get('/api/v1/auth/me');
    expect(session.ok()).toBe(true);
    const account = (await session.json()).user;
    await student.goto('/solicitar');
    await expect(student.getByText('Aún no tienes asignaturas habilitadas')).toBeVisible();
    await page.goto('/login');
    await page.getByRole('link', { name: 'Entrar como profesor', exact: true }).click();
    await expect(page).toHaveURL(/\/inicio$/);
    const upload = await page.request.post('/api/v1/documents/upload', { headers, multipart: {
      title: 'Derivadas para prueba funcional', course, source_reference: 'Texto sintético propio para prueba',
      permission_note: 'Material de prueba creado para esta verificación', authorization_confirmed: 'true',
      file: { name: 'derivadas.txt', mimeType: 'text/plain', buffer: Buffer.from('La derivada mide la tasa de cambio instantánea de una función. La derivada de x al cuadrado es 2x. Para derivar una potencia x elevada a n, se multiplica n por x elevada a n menos uno. La regla de la cadena permite derivar funciones compuestas multiplicando la derivada exterior por la derivada interior.') },
    } });
    expect(upload.status(), await upload.text()).toBe(201); documentId = (await upload.json()).id;
    for (const action of ['process', 'index', 'publish']) {
      const response = await page.request.post(`/api/v1/documents/${documentId}/${action}`, { headers, timeout: 180000 });
      expect(response.status(), await response.text()).toBe(200);
    }
    await page.goto('/accesos');
    await page.getByLabel('Correo del estudiante').fill(account.institutional_email);
    await page.getByLabel('Asignatura', { exact: true }).selectOption(course.toLowerCase());
    const granted = page.waitForResponse(r => r.url().endsWith('/learning/access') && r.request().method() === 'POST');
    await page.getByRole('button', { name: 'Dar acceso', exact: true }).click();
    const grant = await granted; expect(grant.status(), await grant.text()).toBe(201); accessId = (await grant.json()).id;
    await page.evaluate(() => { (document.activeElement as HTMLElement)?.blur(); window.scrollTo(0, 0); });
    await page.screenshot({ path: info.outputPath('accesos-desktop.png'), fullPage: true });
    await student.getByRole('button', { name: 'Actualizar asignaturas' }).click();
    await student.getByLabel('Asignatura y profesor').selectOption(accessId!);
    await student.getByLabel('Quiero pedir').selectOption('HINT');
    await student.getByLabel('Tema', { exact: true }).fill(topic);
    await student.getByLabel('¿Qué quieres entender o resolver?').fill('Una pista para derivar x al cuadrado');
    await student.getByRole('button', { name: 'Buscar apoyo en mis materiales' }).click();
    await expect(student.locator('#student-sources')).toContainText('Derivada');
    await expect(student.getByRole('button', { name: 'Generar contenido', exact: true })).toBeDisabled();
    await expect(student.getByText('La generación todavía no está habilitada.', { exact: false })).toBeVisible();
    await student.evaluate(() => { (document.activeElement as HTMLElement)?.blur(); window.scrollTo(0, 0); });
    await student.screenshot({ path: info.outputPath('solicitar-desktop.png'), fullPage: true });
    await student.setViewportSize({ width: 390, height: 844 });
    await student.evaluate(() => window.scrollTo(0, 0));
    await student.screenshot({ path: info.outputPath('solicitar-mobile.png'), fullPage: true });
    expect(await student.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const saved = await student.request.get('/api/v1/learning/history');
    const identifier = (await saved.json()).items[0].id;
    await student.reload();
    await student.getByRole('button', { name: 'Abrir ' + topic, exact: true }).click();
    await expect(student.locator('#student-sources')).toContainText('Derivada');
    await page.getByRole('button', { name: /Retirar acceso de/ }).click();
    await page.getByRole('button', { name: 'Sí, retirar', exact: true }).click();
    await expect(page.getByText('Acceso retirado.', { exact: true })).toBeVisible();
    expect((await (await student.request.get('/api/v1/learning/courses')).json())).toEqual([]);
    const denied = await student.request.post('/api/v1/learning/prepare', { headers, data: {
      access_id: accessId, topic: 'Derivada', learning_objective: 'Comprender', resource_type: 'EXPLANATION', difficulty: 'basic',
    } });
    expect(denied.status()).toBe(403);
    expect((await student.request.get('/api/v1/learning/history/' + identifier)).status()).toBe(200);
  } finally {
    if (accessId) await page.request.delete('/api/v1/learning/access/' + accessId, { headers });
    if (documentId) await page.request.delete('/api/v1/documents/' + documentId, { headers });
    await studentContext.close();
  }
});
