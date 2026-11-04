'use strict';

// deepknow-Engine DSH 插件（宿主半侧）—— 最小桥接实现。
// 职责：①让插件出现在 DSH 已安装列表并被宿主正常加载；
//      ②注册 ctx.deepknow 只读工具，供人设/其他插件查询技能库位置与版本。
// 真正的能力（身份前提 + 16 项对齐）以 skill 形态存在于 ~/.dsh/skills/deepknow-engine/，
// 由人设挂载触发（dad-profile=他是谁 / deepknow-engine=怎么说）——插件不复制内容，避免双真相源。

const path = require('node:path');
const os = require('node:os');
const fs = require('node:fs');

const SKILL_DIR = path.join(os.homedir(), '.dsh', 'skills', 'deepknow-engine');

function readVersion() {
  try {
    const md = fs.readFileSync(path.join(SKILL_DIR, 'SKILL.md'), 'utf8');
    const m = md.match(/^version:\s*(.+)$/m);
    return m ? m[1].trim() : 'unknown';
  } catch (_) {
    return 'skill-not-found';
  }
}

module.exports = {
  name: 'deepknow-engine',
  inject: [],
  apply(ctx) {
    const log = ctx.logger || console;
    log.info?.('[deepknow-engine] loaded — skills at %s (version %s)', SKILL_DIR, readVersion());

    // 只读服务：任何人设/插件可查询引擎状态，永不写文件（零写入原则）
    ctx.deepknow = {
      skillDir: SKILL_DIR,
      version: readVersion(),
      status() {
        return {
          version: this.version,
          skillInstalled: fs.existsSync(path.join(SKILL_DIR, 'SKILL.md')),
          docs: ['identity-premise(v3.0)', 'stance-alignment-16(v4.0)'],
        };
      },
    };
  },
};
