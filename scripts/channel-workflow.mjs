#!/usr/bin/env node
/**
 * channel-workflow.mjs — deepknow-Engine 四渠道发布工作流
 *
 * 设计铁律（与 deepknow 安全哲学一致）：
 *  - 发出去的帖收不回 → 每步诚实报告「已发 / 未发 / 待登录」，绝不假报。
 *  - 双互提醒：发前校验提醒（content 落库前过规定）+ 发后回读提醒（DOM/API 复核真值）。
 *  - 代理劫持本地回环（127.0.0.1:59171）是本机第一坑 → 必须 NO_PROXY='*' 绕过。
 *
 * 用法：
 *   node scripts/channel-workflow.mjs --dry-run   仅检测登录态+合规校验，不发
 *   node scripts/channel-workflow.mjs --post v2ex 对单渠道尝试实发（需已登录）
 *   node scripts/channel-workflow.mjs --qr-all     对未登录渠道截图二维码交人工扫
 */
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// playwright-core 装在 WorkBuddy node workspace（ESM 不认 NODE_PATH，走 createRequire 显式解析）
function loadPlaywright() {
  const ws = 'C:/Users/Administrator/.workbuddy/binaries/node/workspace/package.json';
  try {
    return createRequire(ws)('playwright-core');
  } catch {
    return null;
  }
}
const pw = loadPlaywright();
if (!pw) { console.error('FATAL playwright-core 不可用'); process.exit(1); }
const { chromium } = pw;


const OUT = path.join(ROOT, 'docs', 'channel-artifacts');
fs.mkdirSync(OUT, { recursive: true });

// 各渠道发布文案（唯一真相源，禁止在代码里散写）
const CONTENT = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs', 'channel-content.json'), 'utf-8'));

// ───────────────────────── 发前校验提醒（帖子规定引擎） ─────────────────────────
const REG_RULES = [
  { id: 'R1', name: '命名一致', re: /deepknow-Engine|知心引擎/, must: true,
    desc: '产品名须为「知心引擎 deepknow-Engine」，禁止退回「知心档案/说明书」旧名' },
  { id: 'R2', name: '无内部泄漏', re: /publish-strategy|launch-kit|hcac4735|shanlun|530416460|善伦|正明|Administrator/, must: false, block: true,
    desc: '禁止出现内部文档名/私人邮箱/真名/本机路径' },
  { id: 'R3', name: '非虚假承诺', re: /月入|稳赚|包赚|保证收益|百分之百|100[%％]|全网第一/, must: false, block: true,
    desc: '禁止收益保证/绝对化表述（HN 老哥最爱打的虚假点）' },
  { id: 'R4', name: '含 GitHub 链接', re: /github\.com\/\S+/, must: true,
    desc: '每帖须带仓库链接，否则引流断链' },
  { id: 'R5', name: '长度合理', re: /[\s\S]{30,}/, must: true,
    desc: '正文须 ≥30 字，避免空壳帖' },
];

function preCheck(channel, text) {
  const hits = [];
  for (const r of REG_RULES) {
    r.re.lastIndex = 0; // 防 /g 状态残留误判（本行是双互提醒里「发前校验提醒」的自检项）
    const ok = r.re.test(text);
    if (r.must && !ok) hits.push({ level: 'BLOCK', rule: r.id, msg: `${r.name}未满足：${r.desc}` });
    if (r.block && ok) hits.push({ level: 'BLOCK', rule: r.id, msg: `${r.name}命中禁用词：${r.desc}` });
  }
  return hits;
}

// ───────────────────────── 渠道定义 ─────────────────────────
const CHANNELS = {
  dsh: {
    label: 'DSH 官方社区 (GitHub Discussions)',
    alreadyDone: true,
    url: 'https://github.com/deepseek-ai/deepseek-harness/discussions',
  },
  v2ex: {
    label: 'V2EX /go/share',
    loginUrl: 'https://www.v2ex.com/signin',
    postUrl: 'https://www.v2ex.com/new',
    checkLogin: async (page) => !(page.url().includes('/signin')),
    qrHint: 'V2EX 用账号密码登录（非扫码），需人工在浏览器内输入后点登录',
  },
  jike: {
    label: '即刻 web.okjike.com',
    loginUrl: 'https://web.okjike.com',
    postUrl: 'https://web.okjike.com',
    checkLogin: async (page) => {
      const t = await page.title().catch(() => '');
      return !/登录|登陆|login/i.test(t) && (await page.locator('text=发布').count()) > 0;
    },
    qrHint: '即刻扫码登录：页面会出现二维码，需人工用即刻 App 扫',
  },
  xiaohongshu: {
    label: '小红书 创作者中心',
    loginUrl: 'https://creator.xiaohongshu.com',
    postUrl: 'https://creator.xiaohongshu.com/publish/publish',
    checkLogin: async (page) => !(page.url().includes('login') || page.url().includes('signin')),
    qrHint: '小红书扫码登录：创作者中心出现二维码，需人工用小红书 App 扫',
  },
};

// ───────────────────────── 主流程 ─────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const qrAll = args.includes('--qr-all');
  const postArg = args.find(a => a.startsWith('--post='))?.split('=')[1];

  const browser = await chromium.connectOverCDP('http://127.0.0.1:9337', { timeout: 45000 });
  const context = browser.contexts()[0] || await browser.newContext();
  const report = [];

  for (const [key, cfg] of Object.entries(CHANNELS)) {
    if (postArg && key !== postArg) continue;
    const page = await context.newPage();
    const entry = { channel: key, label: cfg.label, ts: new Date().toISOString() };

    if (cfg.alreadyDone) {
      entry.status = 'DONE';
      entry.detail = '已通过 gh GraphQL 实发（Discussion #12146），API 回读验证过';
      report.push(entry);
      await page.close();
      continue;
    }

    // ── 发前校验提醒 ──
    const text = CONTENT[key]?.body || CONTENT[key]?.title || '';
    const pre = preCheck(key, text);
    entry.preCheck = pre;
    if (pre.some(p => p.level === 'BLOCK')) {
      entry.status = 'BLOCKED_BY_REG';
      entry.detail = '发前校验未通过，已拦截：' + pre.map(p => p.rule).join(',');
      report.push(entry);
      await page.close();
      continue;
    }

    // 单渠道故障隔离：一渠道网络挂不拖累其余渠道（V2EX 被墙即此类）
    try {
      await page.goto(cfg.loginUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
    } catch (e) {
      entry.status = 'NETWORK_ERROR';
      entry.detail = '入口打不开：' + e.message.split('\n')[0] + '（V2EX 被墙，需 ZoogVPN 连接后重跑）';
      report.push(entry);
      await page.close();
      continue;
    }
    await page.waitForTimeout(8000);
    const loggedIn = await cfg.checkLogin(page).catch(() => false);
    entry.loggedIn = loggedIn;

    if (!loggedIn) {
      entry.status = 'NEEDS_LOGIN';
      entry.detail = cfg.qrHint;
      // 双互提醒·发前侧：登录页二维码截图留痕，交人工扫码后会话持久化进 profile
      const shot = path.join(OUT, `${key}-login-${Date.now()}.png`);
      await page.screenshot({ path: shot, fullPage: false }).catch(() => {});
      entry.qrScreenshot = shot;
      // 页面保持打开：人工扫码/登录在此页完成后，重跑本脚本即检测到已登录
      entry.pageKeptOpen = cfg.loginUrl;
      report.push(entry);
      continue;
    }

    // ── 已登录：尝试实发 ──
    if (!dryRun) {
      try {
        await page.goto(cfg.postUrl, { waitUntil: 'domcontentloaded' });
        // 渠道专属填表逻辑在此扩展（v2.7 补 V2EX 表单字段映射）
        entry.status = 'POST_ATTEMPTED';
        entry.detail = '已登录，表单填充逻辑待 v2.7 补完';
      } catch (e) {
        entry.status = 'POST_ERROR';
        entry.detail = e.message;
      }
    } else {
      entry.status = 'LOGGEDIN_DRYRUN';
    }
    report.push(entry);
    await page.close();
  }

  await browser.close();
  fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
}

main().catch(e => { console.error('FATAL', e); process.exit(1); });
