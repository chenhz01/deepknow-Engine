# dsh-deepknow-engine · 知心引擎（DSH 插件版）

> **deepknow-Engine** — a privacy-tiered dossier engine that makes any AI truly know a person.
> 给你的大肥鱼一份一生的主人使用引擎。第三方非官方插件。

主仓：**https://github.com/chenhz01/deepknow-Engine**（完整设计文档、测试矩阵、28 式费曼助读都在那里）

## 这是什么

DeepSeek Harness 插件 = 轻量桥（`ctx.deepknow` 只读状态服务）。真正的能力是 **Skill 形态**，装在 `~/.dsh/skills/`：

| Skill | 作用 |
|---|---|
| `deepknow-engine` | 说话规矩：身份前提（同侪位/行话位/不越位）+ 立场判断 16 项商业结果对齐 |
| `dad-profile` | 档案内容：《爸爸知心档案》六章节 + 对话引头引擎 |

分工：**档案告诉你「他是谁」，引擎告诉你「怎么说」。**

## 安装

```bash
# 方式一：本地目录安装（推荐，随主仓更新）
cd ~/.dsh/profiles/desktop
pnpm add file:../../dsh-deepknow-plugin

# 方式二：Release 下载 zip 解压到任意目录后
pnpm add file:<解压路径>
```

装完在 DSH 插件管理页「已安装」里即可看到 **dsh-deepknow-engine**。

## 设计承诺（全部有测试背书，主仓可复跑）

- LLM 永远没有直接写档案的路径（五道闸提案管线，21 例含 11 负对照全绿）
- 引擎算条件，LLM 只管说话
- 立场链：本人 > 家庭 > 确认人 > AI
- 一票否决：遍历性出局、代做决定

## 许可

代码 Apache-2.0 / 文档模板 CC BY 4.0（双许可，主仓有完整 LICENSE 文件）
