# 冲星作战手册 · 基于 2026-11-04 GitHub Trending 实测

> 数据源：本周新锐榜（created>=窗口起点 + 按星数降序，25 仓）。本文每条结论都对应榜单上的真实仓位证据。

## 一、今日榜单告诉我们的事实

| # | 仓库 | 星/天 | 品类信号 |
|---|---|---|---|
| 1 | deepseek-ai/dsh-superagent-prototype | 5431 | DSH 生态爆发中 |
| 3 | heydamir/unslop | 1452 | **单文件 agent skill 解决单一痛点** |
| 5 | anhao/ai-pose-gallery-zh | 824 | **中文 + 静态资源库 + 零依赖** |
| 7 | patch-gg/pixelfx | 1008 | agent skill + 效果可演示 |
| 12 | paipiange/nvzhuang | 423 | 中文 AI 资源站 |
| 24 | NiazMorshed2007/reanimate | 212 | agent skill（逆向动画） |
| 25 | jacke-pp/open-yoki | 158 | AI 陪伴/记忆品类 |

**反例（别学）**：今日 daily 榜前 15 里约 10 个是同秒创建、整齐 300 星的破解软件/bot 垃圾仓——刷星生态存在，但 GitHub trending 算法与真人都在排斥它们。慢就是快。

## 二、五个可执行的冲星动作（按优先级）

### 1. 定位：卡进正在涨的品类交叉点 ✅（本仓库已做）
`agent-skills` × `AI 陪伴/记忆` 正是两大热点交叉。发布时 topics 必打：
`agent-skills` `claude-code` `claude-skill` `dsh` `ai-companion` `memory` `persona` `chinese` `prompt-engineering`

### 2. README 前 3 屏定生死（榜单星/天比 ≈ 24 小时窗口）
点进来的人 30 秒内决定 star 与否。必备三件：
- 一句话价值主张（"让任何 AI 真正懂一个具体的人"）
- 效果对比表（没有档案 vs 有档案的真实对话）——unslop 靠前后对比图拿 7.3k
- 30 秒上手命令块（复制即可跑）

### 3. 首发 24 小时渠道（涨星第一波最关键）
- DeepSeek DSH 社区（dshbase / dshpluginhub / 相关 subreddit 与 V2EX）——#1 是 DSH 官方仓证明流量在
- 即刻/V2EX/小红书发「给 AI 管家建了一份我爸妈的档案，效果惊人」贴，附对话截图
- HN 一次（英文标题：*Show HN: A structured dossier format that makes any AI actually know you*）

### 4. 让仓库"可被复制进别人的生活"
- 模板覆盖高频关系（父母/配偶/客户/朋友）✅
- 一键安装脚本 ✅
- 中文仓 **双语 README**（英文 README.en.md 补齐后 HN/reddit 才能传播）

### 5. 持续星发动机（第二周后）
- GitHub Pages 做一个**在线档案生成器 demo**（纯静态，学 ai-pose-gallery-zh 的零依赖打法）
- 欢迎 PR：新模板（宠物/导师/医生）是低成本高参与的贡献入口
- 每次被文章/视频引用，把链接挂进 README「采用案例」区（社会证明滚雪球）

## 三、本仓库已按此手册就位的内容

- ✅ 效果对比表 + 30 秒上手（README）
- ✅ 四类模板 + 一键安装 + 零依赖校验器
- ✅ 双许可（Apache-2.0 + CC BY 4.0）——对商用复用者友好，降低企业采用门槛
- ⬜ README.en.md（待补，发布前完成）
- ⬜ GitHub Pages 在线 demo（第二周）

## 四、预期基线（诚实版）

同类仓（unslop 7 天 7.3k、open-yoki 6 天 950）表明：
- 命中品类 + 首发 24h 渠道做得好：**首周 300-1000 星**是现实区间
- 只发仓不做渠道：**首周 20-50 星**（沉默死亡是默认结局）
- 发表走「A 藏配方 / B 送服务」：核心 schema 与校验器开源引流，增值模板与服务留给后续
