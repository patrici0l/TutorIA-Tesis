import { test, expect } from '@playwright/test';

test('CORE real y archivo sintético: procedencia, revisión y habilitación explícita', async ({ page }, info) => {
  test.skip(process.env.CORE_LIVE_TEST !== '1', 'Solo en base temporal: consulta CORE; el archivo es una muestra sintética, no el artículo real.');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const headers = { 'X-Prototipo-Client': 'web' };
  const course = 'SYN-CORE-' + Date.now();
  let id: string | undefined;
  try {
    await page.goto('/login');
    await page.getByRole('link', {name:'Entrar como profesor',exact:true}).click();
    await expect(page).toHaveURL(/\/inicio$/);
    await page.goto('/fuentes-externas');
    await page.getByRole('link', {name:'CORE · publicaciones',exact:true}).click();
    await page.getByLabel('Tema de la publicación').fill('probability education');
    await page.getByRole('button', {name:'Buscar en CORE',exact:true}).click();
    await page.getByRole('button', {name:/Revisar publicación/}).first().click();
    await expect(page.locator('#core-preview')).toBeVisible();
    await expect(page.getByText('El resumen no se importará como material de estudio.', {exact:false})).toBeVisible();
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.screenshot({path:info.outputPath('core-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:info.outputPath('core-mobile.png'),fullPage:true});
    expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.getByLabel('Archivo original de esta publicación').setInputFiles({name:'ensayo-sintetico.txt',mimeType:'text/plain',buffer:Buffer.from('Archivo sintético para probar el circuito técnico. No es el artículo académico. La probabilidad de un evento está entre cero y uno. En un dado equilibrado cada cara tiene probabilidad uno entre seis. La probabilidad condicional expresa la probabilidad de un evento cuando se conoce otro.')});
    await page.getByLabel('Asignatura', {exact:true}).fill(course);
    await page.getByLabel('¿Qué permiso permite utilizar este archivo?').fill('Muestra sintética propia de ensayo técnico, no reproduce la publicación.');
    await page.getByRole('checkbox').check();
    const imported = page.waitForResponse(r=>r.url().endsWith('/core/import') && r.request().method()==='POST');
    await page.getByRole('button',{name:'Guardar original con su procedencia',exact:true}).click();
    const response=await imported; expect(response.status(),await response.text()).toBe(201);
    const doc=await response.json(); id=doc.id;
    expect(doc.external_source.provider).toBe('core'); expect(doc.published_at).toBeNull();
    expect((await page.request.get('/api/v1/documents/external/core/snapshot/'+id)).status()).toBe(200);
    for (const action of ['process','index']) {
      const r=await page.request.post(`/api/v1/documents/${id}/${action}`,{headers,timeout:180000});
      expect(r.status(),await r.text()).toBe(200);
    }
    await page.getByRole('link',{name:'Revisar y habilitar material →',exact:true}).click();
    await page.getByRole('button',{name:'Ver detalles de '+doc.title,exact:true}).click();
    await expect(page.locator('#publish-source')).toBeDisabled();
    await page.getByText(/Revisar fragmentos ·/).click();
    await page.getByRole('checkbox',{name:/Revisé los fragmentos/}).check();
    await expect(page.locator('#publish-source')).toBeEnabled();
    await page.locator('#document-publication').scrollIntoViewIfNeeded();
    await page.screenshot({path:info.outputPath('aprobacion-mobile.png')});
    const publish=page.waitForResponse(r=>r.url().endsWith('/publish') && r.request().method()==='POST');
    await page.locator('#publish-source').click();
    expect((await publish).status()).toBe(200);
    const prepared=await page.request.post('/api/v1/content/prepare',{headers,data:{course,topic:'Probabilidad de un dado',learning_objective:'Comprender eventos',resource_type:'EXPLANATION',difficulty:'basic'}});
    expect(prepared.status(),await prepared.text()).toBe(201);
    expect((await prepared.json()).sources[0].external_source.provider).toBe('core');
  } finally {
    if(id) await page.request.delete('/api/v1/documents/'+id,{headers});
  }
});
