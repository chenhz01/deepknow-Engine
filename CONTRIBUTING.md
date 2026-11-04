# Contributing

感谢关注 deepknow-Engine（知心引擎）。

## 提交前

1. **隐私红线**：任何 PR / issue / 示例中不得出现真实个人档案数据。示例请用 `examples/` 里的脱敏样例。
2. **零依赖**：本项目只允许 Python 标准库 + Markdown。新功能不得引入 pip 依赖。
3. **Schema 变更走 RFC**：改 `schema/*.json` 请先开 Schema RFC issue，通过后再提交 PR。

## 本地验证

```bash
python scripts/test_v26.py          # 21+ 用例
python scripts/validate.py examples/example-dossier.json
```

## 双许可

代码贡献遵循 Apache-2.0；文档与模板贡献遵循 CC BY 4.0。
