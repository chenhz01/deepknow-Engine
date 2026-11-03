#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知心档案校验器 validate.py v2.0
三重校验：
  1. Schema 校验 —— 六章节结构完整性（v2.0 字段：schema_version/subject_consent/tokens 等）
  2. 基因层联合校验 —— 可选 --gene：确认人/可变性声明/禁否定式预言
  3. 隐私扫描 v2 —— 归一化预处理（全角/分隔符/大写数字折叠）后正则扫描。
     诚实话术：本扫描器对变体（拼音/谐音/拆行）覆盖率有限（红队评估 <40%），
     定位是【降低风险】而非【保护隐私】；publish 模式命中即硬阻断。
用法:
  python validate.py <dossier.json> [--gene gene.json] [--publish]
退出码: 0=通过, 1=结构错误, 2=隐私命中(publish), 3=基因层校验失败
"""
import json, re, sys, argparse

REQUIRED_TOP = ["meta", "who", "money_rules", "projects", "temper", "love_language", "actions"]
REQUIRED_META = ["alias", "relation", "updated", "privacy_level", "schema_version"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CN_NUM = str.maketrans("０１２３４５６７８９－‐‑–—壹贰叁肆伍陆柒捌玖", "0123456789-----一二三四五六七八九")

def normalize(s):
    """归一化：全角→半角、分隔符折叠、大写数字→小写。红队共识：不归一化正则形同虚设。"""
    s = s.translate(CN_NUM)
    s = re.sub(r"[-‐‑–—\s.·]", "", s)
    return s

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
        errs.append("actions 至少 3 条——这是档案的灵魂，不许偷懒")
    for i, r in enumerate(d.get("money_rules", []) or []):
        if isinstance(r, dict) and "enforcement" not in r:
            errs.append(f"money_rules[{i}] 缺少 enforcement")
    sc = meta.get("subject_consent")
    if sc and sc.get("status") == "guardian_confirmed" and not sc.get("scope"):
        errs.append("监护人确认档必须声明授权章节范围（分层同意）")
    return errs

def check_gene(g, d):
    errs, warns = [], []
    gm = g.get("meta", {})
    if gm.get("confirmed_by") not in ("subject", "guardian", "authorized_kin"):
        errs.append("gene.meta.confirmed_by 缺失或非法——基因层必须经主体（或监护人）确认")
    for i, t in enumerate(g.get("temperament", []) or []):
        if "mutability" not in t:
            errs.append(f"gene.temperament[{i}] 缺少 mutability 可变性声明——'不可变'在认知科学上不成立，必须声明慢变等级")
        if any(w in t.get("trait", "") for w in ["固执", "懒", "笨", "坏"]):
            warns.append(f"gene.temperament[{i}] 含评价性词汇——基因层只允许描述性表述")
    for i, b in enumerate(g.get("bottom_lines", []) or []):
        if b.get("negative_prophecy_ban") is not True:
            errs.append(f"gene.bottom_lines[{i}] 缺少 negative_prophecy_ban=true——底线条目禁止用于'他绝不会X'式断言")
    # 联合：基因锚点应与档案 who 一致性提示
    if g.get("meta", {}).get("alias") != d.get("meta", {}).get("alias"):
        warns.append("gene 与 dossier 的 alias 不一致，确认是否同一主体")
    return errs, warns

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
            n = normalize(obj)
            for name, pat in PRIVACY_PATTERNS:
                m = pat.search(n)
                if m:
                    hits.append(f"{path}: 疑似{name} → {m.group(0)[:4]}****")
    walk(d)
    return hits

def main():
    ap = argparse.ArgumentParser(description="知心档案校验器 v2.0")
    ap.add_argument("file")
    ap.add_argument("--gene", help="基因层 gene.json（可选联合校验）")
    ap.add_argument("--publish", action="store_true", help="公开模式：隐私命中即硬阻断")
    args = ap.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        print(f"[FAIL] 无法读取 JSON: {e}")
        sys.exit(1)

    errs = check_schema(d)
    hits = scan_privacy(d)
    warns = []

    if args.gene:
        try:
            with open(args.gene, encoding="utf-8") as f:
                g = json.load(f)
            g_errs, g_warns = check_gene(g, d)
            errs += g_errs
            warns += g_warns
        except Exception as e:
            errs.append(f"基因层读取失败: {e}")

    print(f"== 知心档案校验 v2.0: {args.file} ==")
    for e in errs: print(f"  [结构] ✗ {e}")
    for w in warns: print(f"  [提示] ⚠ {w}")
    for h in hits: print(f"  [隐私] ⚠ {h}")
    if hits:
        print("  说明：扫描器为归一化正则（对拼音/谐音/拆行变体覆盖率有限），定位是降低风险而非保证隐私。")

    if errs:
        print("结果: 结构校验未通过 (exit 1)"); sys.exit(1)
    if args.gene and any("基因层" in e or "gene" in e for e in errs):
        print("结果: 基因层校验未通过 (exit 3)"); sys.exit(3)
    if args.publish and hits:
        print("结果: 公开模式隐私命中，硬阻断 (exit 2)——扫描未过即拒绝发布"); sys.exit(2)
    if hits:
        print("结果: 结构通过；存在隐私命中——仅限 local_only，不得公开")
    else:
        print("结果: 全部通过 ✅")
    sys.exit(0)

if __name__ == "__main__":
    main()
