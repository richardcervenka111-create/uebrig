// End-to-end check of the übrig start page and the app shell, driven with the Playwright library.
// Local:  PW_PATH=/opt/node22/lib/node_modules/playwright BASE_URL=http://127.0.0.1:8080 node tests/e2e.mjs
// CI:     see .github/workflows/pages.yml (job "test"); a red run blocks the deploy.
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PW_PATH || 'playwright');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8080';
const EXE = process.env.CHROME_PATH || undefined; // locally the pre-installed Chromium
const results = [];
function check(name, cond, detail = '') { results.push({ name, ok: !!cond, detail }); if (!cond) console.log('  ✗', name, detail); else console.log('  ✓', name); }
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const browser = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
try {
  const ctx = await browser.newContext({ viewport: { width: 430, height: 860 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'de-CH' });
  const page = await ctx.newPage();
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') pageErrors.push(m.text()); });

  // ---------- start page ----------
  console.log('Startseite');
  await page.goto(BASE + '/index.html');
  await sleep(600);
  check('intro visible, Enter not yet', await page.evaluate(() => !document.getElementById('intro').hidden && getComputedStyle(document.getElementById('enter')).opacity === '0'));
  await sleep(3200);
  check('tagline + Enter visible after animation', await page.evaluate(() => getComputedStyle(document.querySelector('#intro .tag')).opacity === '1' && getComputedStyle(document.getElementById('enter')).opacity === '1'));
  await page.click('#enter'); await sleep(400);
  check('concept sheet opens', await page.evaluate(() => document.getElementById('intro').hidden && !document.getElementById('concept').hidden));
  check('page scroll locked while sheet open', await page.evaluate(() => document.documentElement.classList.contains('locked')));
  // organisations sheet (opened from the concept sheet) scrolls and fits the viewport
  await page.click('#concept [data-open=orgs]'); await sleep(400);
  check('orgs sheet inside viewport and scrollable', await page.evaluate(() => { const s = document.querySelector('#orgs .sheetbox'); const r = s.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight + 1 && s.scrollHeight > s.clientHeight; }));
  check('orgs: 6 entries, tel links', await page.evaluate(() => document.querySelectorAll('#orgList .org').length === 6 && document.querySelectorAll('#orgList a[href^="tel:"]').length >= 3));
  await page.click('#orgs [data-close=orgs]'); await sleep(400);
  await page.click('#concept .press.stamp'); await sleep(400);
  check('concept closed, scroll unlocked', await page.evaluate(() => document.getElementById('concept').hidden && !document.documentElement.classList.contains('locked')));
  check('support button in sticky bar', await page.evaluate(() => { const b = document.querySelector('header.top .support'); return !!b && getComputedStyle(document.getElementById('topbar')).position === 'sticky'; }));
  check('language menu has 4 options', (await page.$$('#langList [data-lang]')).length === 4);

  // check screen
  check('i explains a rule', await page.evaluate(() => { const r = document.querySelectorAll('#checks .check')[1]; r.querySelector('.i').click(); return !r.querySelector('.why').hidden && r.querySelector('.why').textContent.length > 20; }));
  await page.evaluate(() => [...document.querySelectorAll('#checks .check')].slice(0, 6).forEach(b => b.querySelector('.ring').click()));
  check('6/7 → quiet dock', await page.evaluate(() => document.getElementById('cta').classList.contains('quiet') && document.getElementById('countLabel').textContent.trim() === '6 / 7'));
  await page.click('#cta');
  check('quiet dock → shake + glint on 7th', await page.evaluate(() => document.getElementById('cta').classList.contains('shake') && document.querySelectorAll('#checks .check')[6].classList.contains('glint')));
  await sleep(1300);
  await page.evaluate(() => document.querySelectorAll('#checks .check')[6].querySelector('.lbl').click());
  check('7/7 → stamp dock', await page.evaluate(() => document.getElementById('cta').classList.contains('stamp')));
  await page.click('#cta'); await sleep(300);
  check('welcome sheet after 7/7', await page.evaluate(() => !document.getElementById('welcome').hidden && document.getElementById('stepLabel').textContent.includes('2')));
  await page.click('#welcome .press.stamp'); await sleep(1400);

  // form validation
  await page.click('#cta');
  check('empty form → dish hint', await page.evaluate(() => document.getElementById('h-dish').textContent.length > 0));
  await page.fill('#dish', 'Gemüserisotto'); await page.fill('#portions', '12'); await page.fill('#place', 'Länggassstrasse 42'); await page.fill('#business', 'Restaurant Sonne'); await page.fill('#phone', '079 555 11 22'); await page.fill('#email', 'nope');
  await sleep(1300); await page.click('#cta');
  check('bad e-mail → hint', await page.evaluate(() => document.getElementById('h-email').textContent.length > 0));
  await page.fill('#email', 'kueche@sonne.ch'); await sleep(1300); await page.click('#cta');
  check('missing confirmation → hint + glint', await page.evaluate(() => document.getElementById('h-confirm').textContent.length > 0 && document.getElementById('confirm').classList.contains('glint')));
  await page.click('#confirm'); await page.evaluate(() => document.querySelectorAll('.chip')[6].click());
  await sleep(1300); await page.click('#cta'); await sleep(400);
  check('label view with contact line', await page.evaluate(() => document.getElementById('stepLabel').textContent.includes('3') && document.getElementById('t-contact').textContent.includes('Restaurant Sonne · 079 555 11 22 · kueche@sonne.ch')));

  // print: exactly one page
  const pdf = await page.pdf({ format: 'A4' });
  const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
  check('print = 1 page', pages === 1, 'pages=' + pages);

  // log: add, open, edit, save
  await page.click('#cta'); await sleep(200);
  check('log has 1 entry', (await page.$$('#log button')).length === 1);
  await page.click('#log button'); await sleep(300);
  check('detail sheet opens', await page.evaluate(() => !document.getElementById('detail').hidden && document.getElementById('d-title').textContent === 'Gemüserisotto'));
  await page.click('#d-edit'); await sleep(300);
  await page.fill('#dish', 'Gemüserisotto neu'); await page.click('#cta'); await sleep(300);
  check('edit mode → save label', await page.evaluate(() => document.getElementById('ctaFace').textContent.length > 0 && document.getElementById('stepLabel').textContent.includes('3')));
  await page.click('#cta'); await sleep(200);
  check('edited entry replaced, still 1 entry', await page.evaluate(() => document.querySelectorAll('#log button').length === 1 && document.querySelector('#log button').textContent.includes('neu')));

  // languages
  for (const l of ['fr', 'it', 'en']) {
    await page.click('#langBtn'); await page.click(`#langList [data-lang=${l}]`); await sleep(100);
    check(`language ${l} applied`, await page.evaluate((l) => document.documentElement.lang === l && document.querySelector('[data-view=check]').textContent.length > 0 && !/Prüfen/.test(document.querySelector('[data-view=check]').textContent), l));
  }
  // every screen opens at the top
  await page.evaluate(() => window.scrollTo(0, 400)); await page.click('[data-view=check]'); await sleep(100);
  check('new screen opens at top', await page.evaluate(() => scrollY === 0));

  // legacy migration from the old start page
  await page.evaluate(() => { localStorage.clear(); localStorage.setItem('ub_state', JSON.stringify({ biz: 'Alt-Beiz', contact: '031 000 00 00', log: [{ d: '20.09.2026 21:40', dish: 'Linsensuppe', qty: '9 Portionen', to: 'Sleeper', by: '✓' }] })); sessionStorage.setItem('uebrig-intro', String(Date.now())); });
  await page.goto(BASE + '/index.html'); await sleep(800);
  check('legacy log migrated', await page.evaluate(() => document.querySelectorAll('#log button').length === 1 && document.getElementById('business').value === 'Alt-Beiz'));

  check('no page errors on start page', pageErrors.filter(e => !/net::ERR|Failed to load resource|fonts\.g/.test(e)).length === 0, pageErrors.join(' | ').slice(0, 300));

  // ---------- app shell ----------
  console.log('App');
  const errs2 = [];
  const p2 = await ctx.newPage(); p2.on('pageerror', e => errs2.push(String(e)));
  await p2.goto(BASE + '/app/'); await sleep(1500);
  check('app shows login or no-config notice', await p2.evaluate(() => !document.getElementById('v_login').hidden || !document.getElementById('noconfig').hidden));
  check('app: no innerHTML with data (static scan)', !(await p2.evaluate(() => /innerHTML\s*=\s*[^'"`]/.test(document.documentElement.outerHTML))));
  check('app: Datenschutz link present', await p2.evaluate(() => !!document.querySelector('a[href*="datenschutz"]')));
  check('no page errors in app', errs2.length === 0, errs2.join(' | ').slice(0, 300));

  // ---------- datenschutz ----------
  const p3 = await ctx.newPage(); const r3 = await p3.goto(BASE + '/datenschutz.html');
  check('datenschutz.html reachable', r3 && r3.ok());
} finally {
  await browser.close();
}
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
if (failed.length) { console.log('FAILED:', failed.map(f => f.name).join('; ')); process.exit(1); }
