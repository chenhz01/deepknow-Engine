# 竞品对标与发布策略 · 2026-11-04 实测

> 数据源：GitHub Search API 实拉（2026-11-03/04），覆盖 agent-memory / persona card / personal user manual / digital legacy / grief tech 五条赛道 + 头部竞品 README 精读。
> 结论先行：**"让 AI 懂一个真实具体的人"这个格子，GitHub 上没人占。** 最近的邻居都在三个方向上打偏：机器记忆、虚构角色、知识库。

## 一、五条赛道实测地图

### 赛道 A：Agent 记忆基建层（最热闹，但方向不同）

| 仓库 | 星数 | 定位 | 与本仓差异 |
|---|---|---|---|
| mem0ai/mem0 | 68.3k | "The Memory Layer for AI Agents"，生产级记忆基础设施 | 记的是**机器的工作记忆**（对话/决策/状态），不是"一个真人的档案"。无人格、无隐私分级、无主动关怀 |
| TencentCloud/TencentDB-Agent-Memory | 30.4k | 团队级记忆云 | 企业基建，与个人关系档案无交集 |
| MemoriLabs/Memori | 17.4k | 企业级 agent 原生记忆 | 同上 |
| memvid/memvid | 17.4k | 单文件记忆层替代 RAG | 存储形态创新，内容中性 |
| EverMind-AI/EverOS | 13.8k | 本地优先 Markdown 原生记忆 OS（DSH 生态） | **理念最近**（markdown 单一事实源、local-first），但对象仍是 agent 工作记忆。定位互补：它管"记住"，本仓管"懂谁" |
| tigerless-labs/agent-memory | 4.3k | Markdown 真相源+可删缓存+睡眠整理，2 个月 0→4.3k | **增长最快案例**。README 打法值得抄：①不变量（Design commitments）当卖点 ②"enforced by a test, not promised in a doc" 式工程可信话术 |
| MemMachine/MemMachine | 3.1k | 通用记忆层 | 同 mem0 |

**学习点**：这条赛道证明了"agent 记忆"是百亿级关注度的词，但全部在做"agent 记住事"，没人做"AI 懂一个人"。我们是它缺的那块拼图——**互补叙事**（"EverOS/mem0 让 AI 记住一切，deepknow-Engine 让 AI 懂一个人"）比对抗叙事省十倍力气。

### 赛道 B：人格卡 / 角色扮演（形式最近，本质相反）

| 仓库 | 星数 | 定位 | 与本仓差异 |
|---|---|---|---|
| SillyTavern/SillyTavern | 大型前端（300+贡献者） | LLM 前端 + Character Card V2/V3 生态 | 角色卡是**虚构 persona**（ Seraphina 等原创角色），无隐私工程、无真实性约束、主动性全靠 LLM 即兴 |
| liangbannianikun-cmd/kira-switch | 0★（2026-08新建） | 角色卡注入编码 Agent（Codex/Claude Code/DSH） | 形式同路（把人设卡挂进编码 agent），但只做注入不做档案结构。**0 星说明此细分尚无人做成，也说明缺内容**——我们有内容 |
| garretewilliams/utility-persona-templates | 0★ | 9 个 SFW 实用人设模板（CC BY 4.0） | 同为"模板+双许可"打法，体量极小 |

**学习点**：角色卡社区（SillyTavern Discord 等）是被验证过的"人设卡"受众池，但他们是**演**一个不存在的人；我们是**记**一个真实存在的人。反差本身就是传播钩子："我给 AI 建的不是角色卡，是我爸的档案。"

### 赛道 C：第二大脑 / 知识库

| 仓库 | 星数 | 定位 |
|---|---|---|
| AgriciDaniel/claude-obsidian | 16.1k | Claude + Obsidian 自组织第二大脑 |
| inkeep/open-knowledge | 4.8k | AI 原生 markdown IDE / LLM wiki |
| Ar9av/obsidian-wiki | 3.7k | agent 的 Obsidian 数字脑 |

**学习点**：对象是"知识"，我们是"人"。但 claude-obsidian 证明了"基于 Karpathy LLM Wiki 模式"这种**挂靠名人/模式命名**的定位术有效——本仓可挂靠 "agent skills 生态的 human 层"。

### 赛道 D：个人 AI 超级助手（平台层=分发渠道）

openclaw（393k★）、hermes-agent（260k★）、lobehub（83k★）、agency-agents（166k★，人设化专家 agent 合集）。
**学习点**：不打。平台是渠道不是对手——档案是他们生态里的**内容件**（正如 agency-agents 的每个专家=一份结构化人设，证明"结构化人设=可分发资产"模式成立）。

### 赛道 E：悼念科技 / 数字遗产（开源近乎空白）

搜索 grief/memorial/digital legacy/AI loved ones：GitHub 上无成型开源仓（商业闭源：HereAfter AI、StoryFile、Replika 情感记忆）。
**学习点**：**开源侧空白**。"给父母建档"的情感刚需 + 无开源供给 = 最大的差异化窗口，也是中文社区传播（小红书/即刻"给爸妈建档"贴）最狠的情绪点。注意分寸：绝不营销"数字永生"，我们是"活着的人被更好地理解"。

## 二、定位判决

**一句话：本仓不是 memory layer 的竞品，是 memory layer 缺失的"human 层"。**

三栏占位表（建议放 README.en.md 第一屏）：

| | mem0 / EverOS 等记忆层 | SillyTavern 角色卡 | **zhixin-dossier / deepknow-Engine** |
|---|---|---|---|
| 记什么 | agent 的工作记忆 | 一个虚构角色 | **一个真实的人** |
| 隐私 | 无分级 | 无 | **装载时权限+物理隔离+隐私扫描** |
| 主动性 | 无 | LLM 即兴（不可控） | **确定性引擎：配额/冷却/静音/默认 L0** |
| 形态 | SDK/服务 | 前端+卡片 spec | **零依赖 Markdown+Schema，复制即用** |

品类命名权：建议主推 **deepknow-Engine**（英文）+ 品类词 `human dossier for AI` / `know a person, not a persona`。避开红海词 "memory layer"（搜索结果被 mem0 一霸占）。

## 三、从头部竞品 README 抄的四个打法

1. **tigerless/agent-memory 的"设计承诺"体**（2个月4.3k星）：把不变量写成承诺并声明有测试背书。本仓对应改写："权限不是提示词里的承诺——private 章节在 AI 可及范围内**物理不存在**（card-gen 派生，sha256 校验）"。
2. **SillyTavern 的社区资产**：文档站 + Discord + "always free and open sourced" 宣言。第二周起建 Discussions + 贡献模板墙（新模板 PR 是最低成本贡献入口）。
3. **EverOS 的可复现基准**：跑分背书。本仓对应：hooks_engine 的 T1-T10 测试矩阵 + validate.py 三连测，在 README 显性化为"测试背书区"。
4. **claude-obsidian 的挂靠命名**：挂 "Karpathy LLM Wiki pattern"。本仓挂 "agent-skills 生态的 human layer" + DSH 生态（官方仓在榜证明流量所在）。

## 四、发布节奏（在 star-strategy.md 之上修订）

| 阶段 | 动作 | 依据 |
|---|---|---|
| 发布前（本周） | ①补 README.en.md（英文主打 deepknow-Engine）②README 第一屏加三栏占位表 ③"设计承诺"区改写 ④topics 补 `agent-memory` `ai-companion` `family` `privacy` `digital-legacy` | 记忆层词流量大但被占，用对比表借流量 |
| D+0 首发 24h | DSH 社区（dshbase/dshpluginhub）+ V2EX/即刻/小红书「给 AI 建了我爸的档案」贴 + 对话对比截图 | 榜单#1 是 DSH 官方仓，流量实证 |
| D+1~3 | HN：*Show HN: deepknow-Engine – A privacy-tiered dossier that makes any AI truly know a person*（美东周二至周四上午发） | 英文 README 就绪才有资格 |
| D+7~14 | GitHub Pages 在线档案生成器（纯静态）+ 采用案例墙 + Discussions 开放新模板征集 | unslop/ai-pose-gallery-zh 零依赖爆款配方 |
| 持续 | 互补叙事联动：向 EverOS/agent-memory 提 integration issue；角色卡社区发"真实档案 vs 角色卡"反差贴 | 借 68k/13.8k 生态的存量关注 |

**诚实基线**（不变）：首周 300-1000 星=渠道全做到；20-50 星=只发仓不做渠道。刷星仓已泛滥且被算法排斥，慢就是快。

## 五、风险与分寸

- "家人档案"触碰隐私敏感区：README 与所有对外文案必须反复强调 **local-only、脱敏示例、分享前扫描**——这既是伦理也是卖点。
- 悼念场景克制：不承诺"数字永生"，只讲"更好地理解活着的人"。
- 榜单刷星生态（同秒 300 星垃圾仓）证明 trending 会有噪音期，星数不达预期不等于失败，看真人 issue/fork 质量。

---
*正明 × 善伦 · 2026-11-04 · 数据截至 2026-11-03 19:00 UTC*
