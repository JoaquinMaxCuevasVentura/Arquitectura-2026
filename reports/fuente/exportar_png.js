const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 860, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto('file:///home/user/Arquitectura-2026/reports/fuente/estudio_costos_tupiza.html');
  await page.addStyleTag({ content: `
    html { background: #fff; }
    body { width: 860px; padding: 40px 44px 44px; font-size: 10.5pt; }
    .tiles { gap: 10px; }
  `});
  await page.screenshot({ path: '/home/user/Arquitectura-2026/reports/Estudio de costos renderizado Tupiza.png', fullPage: true });
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  console.log('altura CSS px', h);
  await browser.close();
})();
