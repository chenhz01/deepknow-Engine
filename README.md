# 知心档案 zhixin-dossier

> **让任何 AI 真正懂一个具体的人。**
> Make any AI truly *know* one specific person — not a persona, a person.
> 英文别名 **Kinfile**（dossier 在英文语境带"黑材料"联想，双名并行）。

**v2.0 三层架构**（2026-11-04，经 10 身份对抗性脑暴升级）：**基因层**（慢变量基座：身份锚点/气质/底线，主体确认后生效）→ **档案层**（六章节可变内容 + 分章令牌 + sha256 防篡改）→ **卡片层**（装载时生成派生文件，AI 永不接触 private 源内容）。详见 [docs/architecture.md](docs/architecture.md)。

**v2.0 安全突破**：运行时令牌是安全剧场（一次提示注入即穿透）——权限改在**装载时**生效：`card-gen.py` 按令牌预生成派生文件，private 章节物理上不存在于 AI 可及范围内。

[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE-APACHE)
[![License: CC BY 4.0](https://img.shields.io/badge/Docs%20%26%20Templates-CC%20BY%204.0-green.svg)](LICENSE-CC-BY-4.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

---

## 这是什么 / What is this

你的 AI 管家、伴侣机器人、桌宠、客服 Agent——它们都在扮演"懂你"，但每次新会话都失忆。
**知心档案**把"懂一个人"变成一个可维护的**结构化资产**：

- 📁 **一份档案 = 六章节 Markdown + JSON Schema 双载体**：人可读、机器可校验
- 🧠 **任何 Agent 可挂载**：Claude Code skill、DSH NEXT、通用 system-prompt 注入，一份档案多处生效
- 🔒 **隐私内建**：校验器自动扫描真名/手机号/身份证/邮箱，公开发布前强制脱敏
- 🛠 **零依赖**：纯 Python 标准库 + 纯 Markdown，复制即用

## 30 秒上手

```bash
# 1. 一键安装到你的 Agent（自动探测 Claude Code / DSH NEXT）
bash scripts/install.sh          # macOS / Linux
powershell scripts/install.ps1   # Windows

# 2. 在 Agent 里说一句：
#    "用知心档案给我妈妈建一份档案"
#    Agent 会按模板访谈你，生成 dossier.md + dossier.json

# 3. 校验 + 隐私扫描（发布前必跑）
python scripts/validate.py examples/example-dossier.json
```

## 效果对比

| 场景 | 没有档案 | 有档案 |
|---|---|---|
| "我今天好累" | "注意休息哦～"（万能句） | "连轴第三天了，你 23 点后该回锅了——明早那单要不要我帮你砍到 3 件事？" |
| 提理财建议 | 泛泛的风险提示 | 引用他自己定过的杠铃线，温柔但立场坚定地拦 |
| 聊到旧项目 | 一无所知 | 记得哪些在推进、哪些已冻结、为什么 |

差异不在模型，在**档案的颗粒度**。

## 目录结构

```
zhixin-dossier/
├── skill/SKILL.md              # 通用 Agent skill：档案访谈生成器
├── schema/dossier.schema.json  # 档案层 Schema v2.0（令牌/衰减/多视角/同意关卡）
├── schema/gene.schema.json     # 基因层 Schema（慢变量+可变性声明+生死开关）
├── scripts/card-gen.py         # 装载时权限引擎：生成常驻卡/派生档/检索索引
├── templates/                  # 四类人物模板（父母/配偶/客户/朋友）
├── examples/                   # 脱敏示例档案（档案层 + 基因层）
├── scripts/validate.py         # 结构+基因联合校验 + 归一化隐私扫描
├── docs/architecture.md        # 三层架构白皮书（含可证伪判据）
├── docs/brainstorm-log.md      # 10身份对抗脑暴采纳/驳回记录
└── scripts/install.*           # 一键安装
```

## 六章节结构（核心配方）

1. **他是谁** — 身份、角色、在关系网里的位置
2. **钱袋与生死线** — 预算红线、绝不触碰的决策规则
3. **项目主线** — 当前在做什么、已冻结什么、为什么
4. **脾气与雷点** — 讨厌什么、喜欢什么、踩过什么坑
5. **他想怎么被爱** — 沟通偏好、关心方式、越界即错的事
6. **日常动作清单** — 把上面五条翻译成 Agent 的具体行为

> 第 6 章是灵魂：档案不是传记，是**可执行的行为规范**。

## 适用场景

- 个人 AI 管家 / 伴侣 Agent 记住家人
- 客服 Agent 记住大客户（CRM 的温度版）
- 照护场景：记住老人的用药习惯与忌讳
- 团队协作：新成员入职时"读懂"负责人的工作风格

## 隐私与安全

- 档案默认**只存本地**，永不自动上传
- `validate.py` 的隐私扫描会拦截：中国大陆手机号、身份证号、邮箱、精确住址
- 公开分享前请替换真名为化名，示例档案即脱敏范本

## 双许可

| 内容 | 许可 |
|---|---|
| 代码（scripts/、skill/） | [Apache-2.0](LICENSE-APACHE) |
| 模板、文档、示例档案 | [CC BY 4.0](LICENSE-CC-BY-4.0) |

## 致谢

灵感来自 DSH NEXT（DeepSeek Fish）社区的人设卡实践与 Claude agent-skills 生态。

---

*由正明（Zhengming）与善伦维护 · 2026-11-04*
