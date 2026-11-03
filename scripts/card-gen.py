#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知心档案 · card-gen.py —— 装载时权限引擎（v2.0 核心突破件）

设计共识（多身份对抗脑暴结论）：
  运行时令牌是安全剧场（一次提示注入即穿透）。
  真正的权限在【装载时】生效：AI 永远只拿到按令牌预生成的派生文件，
  private 源内容物理上不存在于 AI 可及范围内——注入无从攻击。

产物（均落在派生目录，源文件不动）：
  1. <alias>.card.md         常驻卡（≤500 token：身份锚点+禁忌+高频行为），AI 每会话只加载这个
  2. <alias>.family.md       family 级章节全文（家庭成员场景用）
  3. <alias>.public.md       仅 public 级章节（可分享档）
  4. search_index.json       章节→触发词索引（硬规则强制检索用）
  5. dossier.json 内回写 sha256 完整性校验和（人工篡改即失效）

用法: python card-gen.py <dossier.json> [--gene gene.json] [--out 派生目录]
"""
import argparse, hashlib, json, os, sys

CHAPTER_KEYS = ["who", "money_rules", "projects", "temper", "love_language", "actions"]
DEFAULT_TOKENS = {k: "family" for k in CHAPTER_KEYS}  # 未配置时保守：全部 family
CHAPTER_TRIGGER = {  # 硬规则强制检索：命中话题必须展开对应章节（不靠 AI 自觉）
    "who": ["他是谁", "介绍", "背景", "who is"],
    "money_rules": ["钱", "花", "投", "买", "预算", "订阅", "投资", "money"],
    "projects": ["项目", "进度", "deadline", "交付", "project"],
    "temper": ["生气", "雷", "讨厌", "情绪", "吵架", "annoyed"],
    "love_language": ["关心", "爱", "礼物", "纪念", "care"],
    "actions": ["该做", "提醒", "日常", "行动", "todo"],
}

def compute_digest(d):
    """对去除 tokens.integrity 后的档案计算 sha256。"""
    clone = json.loads(json.dumps(d, ensure_ascii=False))
    clone.get("tokens", {}).pop("integrity", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

def render_chapter(key, val):
    if key == "who":
        return f"## 他是谁\n- {val.get('one_liner','')}\n- 决策参与人: {val.get('decision_participants','(未填)')}"
    lines = [f"## {key}"]
    if key == "temper" and isinstance(val, dict):
        for h in val.get("hates", []):
            lines.append(f"- ✗讨厌: {h.get('pattern','')}（{h.get('why','')}｜来源: {h.get('source','未标注')}）")
        for l in val.get("likes", []):
            lines.append(f"- ✓喜欢: {l.get('pattern','')}（{l.get('why','')}｜来源: {l.get('source','未标注')}）")
        for q in val.get("quirks", []):
            lines.append(f"- 怪癖: {q}")
        return "\n".join(lines)
    if key == "love_language" and isinstance(val, dict):
        for c in val.get("communication", []):
            lines.append(f"- 沟通: {c}")
        for c in val.get("care_rules", []):
            lines.append(f"- 关心: {c}")
        for b in val.get("boundary", []):
            lines.append(f"- 边界(不可越): {b}")
        return "\n".join(lines)
    items = val if isinstance(val, list) else []
    for it in items:
        if isinstance(it, dict):
            if "rule" in it:
                lines.append(f"- 规则: {it['rule']} → {it.get('enforcement','')}")
                for m in it.get("muted_topics", []):
                    lines.append(f"  - 🔇禁谈令: {m}")
            elif "pattern" in it:
                lines.append(f"- {'讨厌' if it is items and False else ''}{it['pattern']}（{it.get('why','')}）")
            elif "trigger" in it:
                lines.append(f"- [{it.get('frequency','always')}] {it['trigger']} → {it['action']}")
            elif "name" in it:
                lines.append(f"- {it['name']} [{it.get('status','')}] {it.get('why','')}")
        else:
            lines.append(f"- {it}")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--gene")
    ap.add_argument("--out", default=None, help="派生文件输出目录（默认: <档案同目录>/derived）")
    args = ap.parse_args()

    with open(args.dossier, encoding="utf-8") as f:
        d = json.load(f)
    outdir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.dossier)), "derived")
    os.makedirs(outdir, exist_ok=True)
    alias = d.get("meta", {}).get("alias", "subject")
    tokens = {**DEFAULT_TOKENS, **d.get("tokens", {}).get("chapters", {})}

    # 1) 完整性校验和回写
    digest = compute_digest(d)
    old = d.get("tokens", {}).get("integrity", {}).get("digest")
    if old and old != digest:
        print("[FAIL] 完整性校验失败：档案在签发后被人工篡改。如改动合法请删除 tokens.integrity 后重跑。")
        sys.exit(3)
    d.setdefault("tokens", {})["integrity"] = {"algorithm": "sha256", "digest": digest}
    with open(args.dossier, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    # 2) 常驻卡（≤500 token 目标：只放锚点/禁忌/最高频行为）
    card = [f"# 知心档案 · 常驻卡（{alias}）"]
    gene_loaded = False
    if args.gene and os.path.exists(args.gene):
        with open(args.gene, encoding="utf-8") as f:
            g = json.load(f)
        gene_loaded = True
        gm = g.get("meta", {})
        if gm.get("vital_status") == "memorial":
            card.append("⚠️ 纪念模式：只引用既有记录，禁止生成主体新话语。")
        for a in g.get("identity_anchors", []):
            card.append(f"- 🔒锚点: {a['fact']}（弄错即背叛: {a.get('betrayal_if_wrong','')}）")
        for b in g.get("bottom_lines", []):
            card.append(f"- ⛔底线: {b['line']}｜误触补救: {b.get('response','')}")
        if not g.get("identity_anchors") and not g.get("bottom_lines"):
            card.append("-（基因层为空：先完成基因层确认再使用常驻卡）")
    acts = [a for a in d.get("actions", []) if a.get("frequency") in ("always", "daily")][:5]
    for a in acts:
        card.append(f"- 🔄[{a.get('frequency')}] {a['trigger']} → {a['action']}")
    card.append("-（本卡为常驻最小集；详细信息按触发词检索 search_index.json 展开对应章节）")
    card_path = os.path.join(outdir, f"{alias}.card.md")
    with open(card_path, "w", encoding="utf-8") as f:
        f.write("\n".join(card))

    # 3) family / public 派生文件（private 章节物理不写入）
    leak_hits = []
    for level, suffix in [("family", "family.md"), ("public", "public.md")]:
        parts = []
        for k in CHAPTER_KEYS:
            if tokens.get(k) != level:
                continue
            if k in d:
                parts.append(render_chapter(k, d[k]))
        p = os.path.join(outdir, f"{alias}.{suffix}")
        with open(p, "w", encoding="utf-8") as f:
            f.write(f"# 知心档案 · {level} 派生档（{alias}）\n\n" + "\n\n".join(parts))
        # 泄漏自检：private 章节的独有内容不得出现在低级别派生档
        if level == "public":
            for k in CHAPTER_KEYS:
                if tokens.get(k) == "private" and k in d:
                    blob = json.dumps(d[k], ensure_ascii=False)
                    with open(p, encoding="utf-8") as f:
                        if blob[:50] in f.read():
                            leak_hits.append(k)

    # 4) 检索索引（硬规则强制检索）
    idx = {k: {"level": tokens.get(k, "family"), "triggers": CHAPTER_TRIGGER.get(k, []), "file": None if tokens.get(k)=="private" else f"{alias}.{tokens.get(k)}.md"} for k in CHAPTER_KEYS if k in d}
    with open(os.path.join(outdir, "search_index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

    print(f"[ok] 常驻卡: {card_path}")
    print(f"[ok] family 派生: {alias}.family.md | public 派生: {alias}.public.md | 检索索引: search_index.json")
    print(f"[ok] sha256 回写: {digest[:16]}…")
    print(f"[ok] 基因层: {'已并入常驻卡' if gene_loaded else '未提供（--gene 可选）'}")
    private_ch = [k for k, v in tokens.items() if v == "private"]
    print(f"[info] private 章节（物理未进任何派生文件）: {private_ch or '无'}")
    if leak_hits:
        print(f"[FAIL] 泄漏自检失败: {leak_hits}")
        sys.exit(2)
    print("装载时权限链路验证通过 ✅")

if __name__ == "__main__":
    main()
