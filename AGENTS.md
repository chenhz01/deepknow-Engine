<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# AGENTS.md — deepknow-Engine 仓库契约

> 本文件是**最高优先级工程规范**，所有开发者（含 AI Agent）改动本仓前必须遵守。
> 只放「不能违背的不变量」和「去哪找细节」的指针；长流程不写在这里。
> 分层做法学自 `ranxianglei/billion-context`（Tier A/B + 按需开文件），
> 一致性清单学自 `vercel-labs/agent-browser`（改一处同更 N 处）。

## Tier A — 每会话必读（不变量）

1. **双许可分区**：代码 Apache-2.0（`LICENSE-APACHE`），文档与模板 CC BY 4.0（`LICENSE-CC-BY-4.0`）；**本仓不提供 MIT**。新增文件须带正确 SPDX 标记。
2. **隐私是装载时权限，不是提示词承诺**：`private` 章节物理上不得进入 AI 可及范围；`card-gen.py` 派生脱敏卡，`validate.py` 做隐私扫描。任何让 LLM 直接读/写档案的改动一律拒绝。
3. **fail-closed**：`scripts/test_v26.py`（含负对照）与 `scripts/validate.py` 必须全绿；注入/越权/主语错位整包拒，退出码非 0 就是拒绝，不许「降级放行」。
4. **数字必可复跑**：README 中任何测试数/验收数都要有对应脚本；没有脚本支撑的宣称视为 bug。
5. **零依赖**：核心产物是 Markdown + JSON Schema + Python 标准库；`dsh-plugin/` 是可选轻量桥，不得反向依赖它。
6. **隐私边界**：本仓是公开发布的独立项目，**不含任何真实人物档案、私有记忆或内部规则**；`examples/` 只能放虚构样例。

## Tier B — 按需打开（don't guess at a procedure, open the file）

| 遇到这件事 | 打开 |
|---|---|
| 改档案结构 / 六章节 | `schema/dossier.schema.json` + `templates/` 四份模板 + `scripts/validate.py` |
| 改安全闸 / 五道闸 | `scripts/proposal.py`、`scripts/test_v26.py` 的 N1–N11 负对照、`docs/architecture.md` |
| 改主动关怀配额 / 冷却 / 静音 | `scripts/hooks_engine.py` + `schema/hooks.schema.json` + `docs/dialogue-hooks.md` |
| 改身份前提 / 立场判断 16 项 | `docs/v3.0-identity-premise.md`、`docs/v4.0-stance-alignment-16.md`、`skill/SKILL.md` |
| 改引头引擎 / 对话流程 | `prompts/extraction-contract-v1.md` + `docs/dialogue-hooks.md` |
| 改 DSH 插件桥 | `dsh-plugin/index.js`、`dsh-plugin/package.json`、`dsh-plugin/README.md` |
| 改安装脚本 | `scripts/install.sh` **和** `scripts/install.ps1`（双平台成对） |
| 赛道 / 版本 / 路线图 | `docs/competitor-analysis.md`、`docs/star-strategy.md`、`docs/v2.6-update-proposal.md` |

**规则**：遇到流程性问题，先按上表开文件，不要凭记忆猜步骤；文件里没有的，去 issue 问，不要自行发明。

## 一致性契约（改一处，必须同更 N 处）

| 你改了 | 必须同更 |
|---|---|
| 任一 `schema/*.json` | `templates/` 四份模板 + `scripts/validate.py` + `examples/example-dossier.json` + `skill/SKILL.md` |
| 任一 `scripts/*.py` 的判定 | `scripts/test_v26.py` 对应正/负对照 + `docs/architecture.md` 承诺表 |
| 首屏 / 30 秒上手 | `README.md` **和** `README.en.md`（中英成对） |
| 安装方式 | `scripts/install.sh` + `scripts/install.ps1` + 两份 README + `dsh-plugin/README.md` |
| 许可或 SPDX | `LICENSE-APACHE` / `LICENSE-CC-BY-4.0` / 两份 README 的 badge 行 |
| 隐私承诺 C1–C6 | `docs/architecture.md` 承诺表 + 对应测试 + 两份 README |

提交前自查：动了左列任意一项而右列没动 = 不允许提交。
**分发双通道**：社区版（clone + install 脚本）与 DSH 插件版（`dsh-plugin/`）必须保持同一套 schema 与承诺，不得各说各话。
