#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知心档案校验器 validate.py
双重校验：
  1. Schema 校验 —— 六章节结构完整性（内置精简校验，零依赖）
  2. 隐私扫描   —— 真实手机号/身份证/邮箱/精确地址检测（公开发布闸门）
用法:
  python validate.py <dossier.json> [--publish]
退出码: 0=通过, 1=结构错误, 2=隐私命中(publish 模式下)
"""
import json, re, sys, argparse

# ---------- 内置精简 schema 校验（不引入 jsonschema 依赖） ----------
REQUIRED_TOP = ["meta", "who", "money_rules", "projects", "temper", "love_language", "actions"]
REQUIRED_META = ["alias", "relation", "updated", "privacy_level"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def check_schema(d):
    errs = []
    for k in REQUIRED_TOP:
        if k not in d:
            errs.append(f"缺少顶层章节: {k}")
    meta = d.get("meta", {})
    for k in REQUIRED_META:
        if k not in meta:
            errs.append(f"meta 缺少字段: {k}")
    if "updated" in meta and not DATE_RE.match(str(meta["updated"])):
        errs.append("meta.updated 须为 YYYY-MM-DD")
    if isinstance(d.get("actions"), list) and len(d["actions"]) < 3:
        errs.append("actions（日常动作清单）至少 3 条——这是档案的灵魂，不许偷懒")
    if isinstance(d.get("money_rules"), list):
        for i, r in enumerate(d["money_rules"]):
            if isinstance(r, dict) and "enforcement" not in r:
                errs.append(f"money_rules[{i}] 缺少 enforcement（AI 发现越线时的标准动作）")
    return errs

# ---------- 隐私扫描 ----------
PRIVACY_PATTERNS = [
    ("中国大陆手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("身份证号", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("邮箱地址", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("精确住址线索", re.compile(r"(省|市|区|路|街道|号院?)\s*\d{1,4}\s*号")),
]

def scan_privacy(d):
    hits = []
    def walk(obj, path="$"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            for name, pat in PRIVACY_PATTERNS:
                m = pat.search(obj)
                if m:
                    hits.append(f"{path}: 疑似{name} → {m.group(0)[:4]}****")
    walk(d)
    return hits

def main():
    ap = argparse.ArgumentParser(description="知心档案校验器")
    ap.add_argument("file", help="dossier.json 路径")
    ap.add_argument("--publish", action="store_true", help="公开分享模式：隐私命中即失败")
    args = ap.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        print(f"[FAIL] 无法读取 JSON: {e}")
        sys.exit(1)

    errs = check_schema(d)
    hits = scan_privacy(d)

    print(f"== 知心档案校验: {args.file} ==")
    for e in errs:
        print(f"  [结构] ✗ {e}")
    for h in hits:
        print(f"  [隐私] ⚠ {h}")

    if errs:
        print("结果: 结构校验未通过 (exit 1)")
        sys.exit(1)
    if args.publish and hits:
        print("结果: 公开模式下隐私命中，禁止发布 (exit 2)")
        sys.exit(2)
    if hits:
        print("结果: 结构通过；存在隐私命中——仅限 local_only，不得公开")
        sys.exit(0)
    print("结果: 全部通过 ✅")
    sys.exit(0)

if __name__ == "__main__":
    main()
