// 四渠道登录态探测（零依赖 playwright-core + CDP；只读，不提交任何内容）
// 运行：env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy NO_PROXY="127.0.0.1,::1,localhost" node probe.mjs
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('C:/Users/Administrator/.workbuddy/binaries/node/workspace/node_modules/playwright-core');

const TARGETS = [
  { id: 'v2ex',      url: 'https://www.v2ex.com/new',                              loginHint: ['/signin', '登录', 'Sign In'] },
  { id: 'jike',      url: 'https://web.okjike.com',                               loginHint: ['登录', '扫码'] },
  { id: 'xiaohongshu', url: 'https://creator.xiaohongshu.com/publish/publish',     loginHint: ['登录', '扫码', 'signin'] },
];

const out = [];
const browser = await chromium.connectOverCDP('http://127.0.0.1:9337');
const ctx = browser.contexts()[0];
const page = await ctx.newPage();
for (const t of TARGETS) {
  try {
    await page.goto(t.url, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.waitForTimeout(4000);
    const info = await page.evaluate(() => ({
      url: location.href,
      title: document.title,
      textLen: (document.body?.innerText || '').length,
      head: (document.body?.innerText || '').slice(0, 180).replace(/\s+/g, ' '),
      inputs: [...document.querySelectorAll('input,textarea,[contenteditable=true]')].length,
    }));
    const login = t.loginHint.some(h => info.url.toLowerCase().includes(h.toLowerCase()) || info.head.includes(h)) || /signin|login/i.test(info.url);
    out.push({ id: t.id, ...info, logged_in_guess: !login, note: login ? '登录墙' : '未见登录墙，需人工复核' });
  } catch (e) {
    out.push({ id: t.id, error: String(e).slice(0, 160) });
  }
}
await page.close();
console.log(JSON.stringify(out, null, 1));
await browser.close();
process.exit(0);
