# 知心档案 deepknow-dossier —— 给你的大肥鱼一份一生的主人使用说明书

> **Know a person, not a persona.** 让大肥鱼真正懂一个具体的人——不是演，是懂。
> **The human layer of the agent-skills ecosystem.** 英文主名 **deepknow**（产品名 deepknow-Engine，英文版见 [README.en.md](README.en.md)）。

[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE-APACHE)
[![License: CC BY 4.0](https://img.shields.io/badge/Docs%20%26%20Templates-CC%20BY%204.0-green.svg)](LICENSE-CC-BY-4.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-21%2B%20cases%20green-brightgreen.svg)](scripts/test_v26.py)

## 一张表看懂我们在哪（第一屏 · 三栏定位表）

| | 记忆层（mem0 / EverOS…） | 角色卡（SillyTavern…） | **知心档案 / deepknow-Engine** |
|---|---|---|---|
| 记什么 | agent 的工作记忆 | 一个虚构角色 | **一个真实的人** |
| 隐私 | 无分级 | 无 | **装载时权限 + 物理隔离 + 隐私扫描** |
| 主动性 | 无 | LLM 即兴（不可控） | **确定性引擎：配额/冷却/静音/默认 L0** |
| 形态 | SDK / 服务 | 前端 + 卡片 spec | **零依赖 Markdown + Schema，复制即用** |

> 一句话：本仓不是 memory layer 的竞品，是 **memory layer 缺失的 human 层**。

---

## 🔥 为什么是它：三个钩子

### 钩子一 · 怎么帮你的大肥鱼更真人

你的大肥鱼每天陪你聊、帮你干活，但它每次睡醒（新会话）都把你忘干净，说出来的话永远像客服。
**解法不是换更大的模型，是给它一份《主人使用说明书》。**

| 场景 | 没有说明书 | 有说明书 |
|---|---|---|
| "我今天好累" | "注意休息哦～"（万能句） | "连轴第三天了，你 23 点后该回锅了——明早那单要不要我帮你砍到 3 件事？" |
| 提理财建议 | 泛泛的风险提示 | 引用他自己定过的杠铃线，温柔但立场坚定地拦 |
| 聊到旧项目 | 一无所知 | 记得哪些在推进、哪些已冻结、为什么 |
| 深夜 23 点还在跑 | 照常回消息 | 引擎算到静音时段，先劝歇再收尾 |

**情感不是装出来的，是说明书喂出来的。** 大肥鱼说的每一句"懂你"都有档案出处：它知道你的雷点、你的未完线、你想被怎么对待——所以一句顶一万句。这就是"由使用说明书而产生基础情感"：不是让 AI 学会抒情，是让它有东西可依据。

说明书 = **六章节结构化档案**（他是谁/钱袋生死线/项目主线/脾气雷点/他想怎么被爱/日常动作清单），Markdown 人可读 + JSON Schema 机器可校验，五层安全架构（基因层→档案层→卡片层→引头引擎→更新回路）经 30+ 场多身份对抗脑暴锻造。

### 钩子二 · 以后所有的对话 AI 都要装这个

这不是大话，是趋势判断：**"agent 记忆"赛道的军备竞赛已经打出 68k 星**（mem0）， EverOS 13.8k、tigerless 4.3k 全在做"AI 记住事"——但没有一家做"AI 懂一个真实的人"。机器的工作记忆（memory layer）和主人的说明书（human layer）是两层东西，前者已经卷成红海，后者**整条赛道还是空地**。

- 🧠 **任何 Agent 可挂载**：DSH NEXT、Claude Code、桌宠、客服机器人——一份说明书多处生效
- 📁 纯 Markdown + 纯 Python 标准库，零依赖，复制即用，永不上传
- 🔒 隐私内建：AI 永远拿不到你不让它拿的部分（装载时权限，不是提示词里的口头承诺）

### 钩子三 · 持续维护升级 · 两个商用版本 · 厂家合作开放

- 🔁 **持续维护**：v2.0 三层架构 → v2.5 对话引头 → v2.6 档案更新回路（2026-11-04，五道闸 21 例验收全绿）。路线图公开：v2.7 = supersede 链 / 多设备 export-import / 更多文化情景包。每一个版本都过对抗性脑暴+实跑验收，不接受"应该能跑"。
- 🏪 **两个商用版本**在路线图上：**Pro 模板包**（照护机构版 / 客户温度版 CRM）与**定制建档服务**（子女给父母建档访谈代做）。社区版永久免费开源，商用版养活持续开发。
- 🤝 **厂家合作**：桌面 AI / 陪伴机器人 / 客服系统厂商预装合作洽谈 → **hcac4735@agent.qq.com**（注明 deepknow）。

---

## 30 秒上手

```bash
# 1. 一键安装到你的 Agent（自动探测 Claude Code / DSH NEXT）
bash scripts/install.sh          # macOS / Linux
powershell scripts/install.ps1   # Windows

# 2. 在 Agent 里说一句：
#    "用知心档案给我妈妈建一份说明书"
#    Agent 会按模板访谈你，生成 dossier.md + dossier.json

# 3. 校验 + 隐私扫描（发布前必跑）
python scripts/validate.py examples/example-dossier.json
```

## 设计承诺（每一条都有测试背书，不是文档里的口头承诺）

> 抄 tigerless/agent-memory 的话术并升级：**enforced by a test, not promised in a doc.** 测试矩阵全开源，谁都可以跑：`python scripts/test_v26.py`（21 例含 11 负对照）+ `python scripts/validate.py examples/example-dossier.json`（结构+隐私扫描）。

| # | 承诺 | 机制 | 测试背书 |
|---|---|---|---|
| C1 | AI 永远读不到 private 章节 | card-gen 装载时派生脱敏卡，private 物理不在 AI 可及范围 | 派生件 sha256 校验 + validate 三连测 |
| C2 | AI 永远无法直接写档案 | 它只能产出提案 JSON，写入路径全是确定性代码 | 五道闸 N1-N11 负对照（注入/越权/主语错位整包拒 exit 2） |
| C3 | 档案被篡改当场暴露 | 入库重签 sha256 digest，装载前校验 | 篡改中止测试（exit 3，全部拒绝执行） |
| C4 | 未经你签字的提案不生效 | 人工确认闸 + 惰性过期（用药 24h/生活 14 天） | 过期拒批 + 连批≥3 强制二次确认测试 |
| C5 | 行为指令进不了档案 | after 字段行为动词检测 + ANSI 清洗 | 指令注入毒包 fixture 三件，全拒 |
| C6 | 主动关怀永不变成骚扰 | 默认 L0 永不主动；配额 3/日 + 冷却 2h + 静音时段，全部硬编码于确定性引擎（LLM 无权触碰闸门） | 引擎级设计见 [docs/dialogue-hooks.md](docs/dialogue-hooks.md)；v2.7 计划补独立测试文件 |

**诚实的边界**：隐私扫描对变体（拼音/谐音/拆行）覆盖率有限——我们承诺"降低风险"，不承诺"保证隐私"。档案是你家的，钥匙也只在你手里。

## 版本演进（全部实跑验收，不接受纸面功能）

| 版本 | 突破 | 验收 |
|---|---|---|
| v2.0 三层架构 | 装载时权限：private 章节**物理不存在**于 AI 可及范围（card-gen 派生 + sha256 防篡改） | 10 身份对抗脑暴 + 校验器三连测 |
| v2.5 对话引头 | 档案从静态知识变成"会自然开口的懂你"；默认永不主动（L0），引擎确定性执行配额/冷却/静音 | 12 身份 × 36 场深审 + 引擎 T1-T10 全绿 |
| v2.6 更新回路 | 档案在人工闸门下生长：对话→提案（AI 零写入）→确认→扫描→入库，**你的档案你签字** | 8 身份 24 场对攻 + 五道闸 21 例含 11 负对照全绿 |

---

# 竞品对标（GitHub 五路实测，2026-11-04）

> 数据源：GitHub Search API 实拉五条赛道 + 头部竞品 README 精读。完整数据见 [docs/competitor-analysis.md](docs/competitor-analysis.md)。

## 一、赛道地图（五路实测）

| 赛道 | 头部 | 星数 | 判决 |
|---|---|---|---|
| A. Agent 记忆基建 | mem0 / TencentDB / Memori / memvid / **EverOS** / **tigerless** | 68.3k / 30.4k / 17.4k / 17.4k / 13.8k / 4.3k | 全做"agent 记住事"，无人做"懂谁"→ **互补不打对抗** |
| B. 人格卡/角色扮演 | SillyTavern / kira-switch / utility-persona-templates | 大型前端 / 0★ / 0★ | 演一个不存在的人 vs 记一个真实存在的人 → **反差即钩子** |
| C. 第二大脑/知识库 | claude-obsidian / open-knowledge / obsidian-wiki | 16.1k / 4.8k / 3.7k | 对象是知识不是人 → 挂靠"agent-skills 生态 human 层" |
| D. 个人 AI 平台 | openclaw / hermes-agent / agency-agents / lobehub | 393k / 260k / 166k / 83k | 平台是渠道不是对手 → **档案是它们生态里的内容件** |
| E. 悼念科技/数字遗产 | 开源近乎空白（商业闭源：HereAfter AI 等） | — | **最大差异化窗口**，分寸：理解活着的人，绝不碰"数字永生" |

## 二、头部竞品精读（四个可直接抄的打法）

1. **tigerless/agent-memory**（2 个月 0→4.3k）：把不变量写成"设计承诺"并声明有测试背书（"enforced by a test, not promised in a doc"）。本仓对应：*"权限不是提示词里的承诺——private 章节在 AI 可及范围内物理不存在（card-gen 派生，sha256 校验，21 例对抗测试背书）"*。
2. **EverOS**（13.8k，DSH 生态）：Markdown 单一事实源 + local-first，理念最近但对象是 agent 工作记忆。互补叙事："EverOS 让大肥鱼记住一切，知心档案让大肥鱼懂一个人。"
3. **SillyTavern**：文档站 + Discord + "always free and open sourced" 宣言养出角色卡大生态。第二周起开 Discussions + 新人物模板 PR 征集（最低成本贡献入口）。
4. **claude-obsidian**（16.1k）：挂靠 Karpathy LLM Wiki 模式命名获流量。本仓挂靠 "agent-skills 生态的 human layer" + DSH 官方生态。

## 三、定位判决与品类命名权

**一句话：本仓不是 memory layer 的竞品，是 memory layer 缺失的 human 层。**

| | mem0 / EverOS 等记忆层 | SillyTavern 角色卡 | **deepknow-dossier / deepknow-Engine** |
|---|---|---|---|
| 记什么 | agent 的工作记忆 | 一个虚构角色 | **一个真实的人** |
| 隐私 | 无分级 | 无 | **装载时权限+物理隔离+隐私扫描** |
| 主动性 | 无 | LLM 即兴（不可控） | **确定性引擎：配额/冷却/静音/默认 L0** |
| 形态 | SDK/服务 | 前端+卡片 spec | **零依赖 Markdown+Schema，复制即用** |

**品类命名权**：避开被 mem0 霸占的红海词 "memory layer"，主推 **deepknow**（英文，产品名 deepknow-Engine）+ 品类词 `human dossier for AI` / `know a person, not a persona`。

---

## 六章节结构（核心配方）

1. **他是谁** — 身份、角色、在关系网里的位置
2. **钱袋与生死线** — 预算红线、绝不触碰的决策规则
3. **项目主线** — 当前在做什么、已冻结什么、为什么
4. **脾气与雷点** — 讨厌什么、喜欢什么、踩过什么坑
5. **他想怎么被爱** — 沟通偏好、关心方式、越界即错的事
6. **日常动作清单** — 把上面五条翻译成 Agent 的具体行为

> 第 6 章是灵魂：说明书不是传记，是**可执行的行为规范**。

## v2.6 档案更新回路：说明书会生长，但每一笔你签字

```
对话 → ①提取（宿主Agent按契约） → ②提案（AI零写入） → ③人工确认 → ④扫描 → ⑤入库
```

AI 永远没有直接写档案的路径——它只能产出"提案"，你确认后才入库，入库前还要过隐私扫描+行为动词检测+主语校验三道确定性代码闸。硬边界：基因层不进提案回路；删除不物理删；第三方信息默认不提取；本人随时否决权高于确认人。

```bash
python scripts/proposal.py submit 提案包.jsonl --dir proposals/     # 闸②
python scripts/proposal.py review --dir proposals/                  # 闸③：惰性过期（用药24h/生活14天）
python scripts/proposal.py approve --dir proposals/ --ids p-20261104-001   # 单批≤5，连批≥3需二次确认
python scripts/proposal.py ingest --dossier 档案.json --dir proposals/ --cardgen scripts/card-gen.py  # 闸④⑤
```

## 隐私与安全

- 说明书**只存本地**，永不自动上传
- 五层防护：装载时权限（private 物理隔离）→ 确定性引头引擎 → 提案五道闸 → 归一化隐私扫描 → sha256 防篡改
- 诚实声明：扫描器对变体（拼音/谐音/拆行）覆盖率有限，定位是**降低风险**而非**保证隐私**；公开发布前请替换真名

## 目录结构

```
deepknow-dossier/
├── skill/SKILL.md               # 通用 Agent skill：档案访谈生成器
├── prompts/extraction-contract-v1.md  # 闸① 提取契约（宿主 Agent 调用规范）
├── schema/dossier.schema.json   # 档案层 Schema v2.0
├── schema/gene.schema.json      # 基因层 Schema
├── schema/hooks.schema.json     # 对话引头 Schema v2.5
├── schema/proposal.schema.json  # 更新提案 Schema v2.6（subject/confirmer 分离）
├── scripts/card-gen.py          # 装载时权限引擎
├── scripts/hooks_engine.py      # 对话引头引擎
├── scripts/proposal.py          # v2.6 提案闸门链（submit/review/approve/ingest）
├── scripts/test_v26.py          # 五道闸验收（21 例含 11 负对照）
├── scripts/validate.py          # 结构+基因联合校验+隐私扫描
├── templates/                   # 四类人物模板（父母/配偶/客户/朋友）
├── examples/                    # 脱敏示例（含 3 个红队毒包）
├── docs/28-feynman-styles.md    # 28 种费曼助读完整版
├── docs/competitor-analysis.md  # 竞品对标全量数据
├── docs/architecture.md         # 三层架构白皮书
└── docs/dialogue-hooks.md       # v2.5 引头引擎设计
```

---

## 🎓 尾部彩蛋：28 种费曼助读——换 28 个角度讲清这份说明书

> 不会跟家人解释这玩意是干嘛的？我们替你准备了 28 种讲法。完整版（每式含定义/公式/知心档案示例/适用场景/翻车点）见 [docs/28-feynman-styles.md](docs/28-feynman-styles.md)。

**第一组 · 极小化**——把听众和篇幅压到极限：01 五岁版本（"机器人睡一觉就忘事，小本本让它睡醒接着疼爸爸"）/ 02 一句话电梯 / 03 热搜标题党 / 04 祖母测试 / 05 外星人简报 / 06 三十楼电梯 / 07 emoji 独白

**第二组 · 极大化**——把尺度放到宇宙级：08 文明存亡（"AI 时代的家庭记忆防火墙"）/ 09 亿年尺度 / 10 国运比喻 / 11 史诗战争 / 12 神话重述 / 13 末日广播 / 14 百亿估值（"如果有人要买走你全家对彼此的了解，你卖吗？"）

**第三组 · 极端具体化**——把抽象钉死在具体里：15 一颗花生 / 16 菜市场砍价 / 17 水管工上门 / 18 宿舍卧谈 / 19 一天时间线 / 20 反面灾难 / 21 钞票流向

**第四组 · 极端错位**——放在最不该放的地方：22 武侠秘籍（《主人说明书·上卷：知妻莫若档》）/ 23 相声对口 / 24 药品说明书（"用法用量：每次会话装载一份；禁忌：不扫描不发布"）/ 25 法庭对质 / 26 相亲简历 / 27 Boss 战攻略 / 28 聊天记录（"大肥鱼：连轴第三天了，23 点了，回锅吧——档案出处：日常动作清单 §3"）

## 商用与合作

| 版本 | 内容 | 价格 |
|---|---|---|
| 社区版（本仓） | 全部核心能力，永久免费开源 | 免费 |
| Pro 模板包（路线图） | 照护机构版 / 客户温度版 CRM | 洽谈 |
| 定制建档服务 | 子女给父母建档访谈代做 | 洽谈 |

厂家预装合作 / 商务洽谈：**hcac4735@agent.qq.com**（注明 deepknow）

## 双许可

| 内容 | 许可 |
|---|---|
| 代码（scripts/、skill/） | [Apache-2.0](LICENSE-APACHE) |
| 模板、文档、示例档案 | [CC BY 4.0](LICENSE-CC-BY-4.0) |

## 致谢

灵感来自 DSH NEXT（DeepSeek Fish，大肥鱼）社区的人设卡实践与 Claude agent-skills 生态。竞品数据实拉自 GitHub Search API（2026-11-04）。

---

*由正明（Zhengming）与善伦维护 · 2026-11-04 · 每一笔变更都有实跑证据*
