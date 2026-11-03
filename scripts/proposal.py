#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知心档案 · proposal.py —— v2.6 档案更新回路（闸②③④⑤）

五道闸中本脚本负责后四道（闸①提取=宿主 Agent 按 prompts/extraction-contract-v1.md 执行）：
  ② submit   提案校验（契约校验+行为动词+亲属词+隐私归一扫描+ANSI 清洗）→ 落分片 jsonl。LLM 零写入。
  ③ review   惰性过期判定（随读判定，禁后台定时器）+ 摘要先行 + strip ANSI 展示
     approve  批准：单批 ≤5；一次 ≥3 需 --confirm-batch 二次确认；过期拒批
  ④ (ingest 内) 扫描复验：隐私正则+行为动词+亲属词主语规则，任一命中 exit 2
  ⑤ ingest   完整性校验（档案签发后被篡改即中止）→ timeline 追加 → card-gen 重派生
             （scrub env + 输入白名单）→ 输入清单哈希落 derived/ingest-manifest.json

设计共识（对攻脑暴定案）：
  - LLM 永远没有直接写档案的路径，只能产出提案；闸门全部是确定性代码
  - 生命周期惰性随读判定——Windows 无 cron，任何后台定时器都是沉默失败温床
  - 过期不销毁：冻结转摘要（"两周回顾 N 件事等你勾选"）
  - confidence 不参与排序（自报置信度与真实准确率相关性弱），仅存档

用法:
  python proposal.py submit   <proposals.jsonl> --dir <提案目录>
  python proposal.py review   --dir <提案目录> [--summary]
  python proposal.py approve  --dir <提案目录> --ids p1,p2 [--confirm-batch]
  python proposal.py ingest   --dossier <dossier.json> --dir <提案目录> [--cardgen <card-gen.py路径>]
  python proposal.py lifecycle --dir <提案目录>

退出码: 0=通过 | 1=结构错误 | 2=安全命中(注入/隐私/越权/亲属词) | 3=完整性失败 | 4=确认策略拒绝 | 5=生命周期拒绝
诚实声明：行为动词/亲属词检测是启发式 denylist，对变体覆盖率有限；定位是【提高攻击成本】，不是【保证安全】。
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys

SCHEMA_VERSION = "proposal/1.0"
CHAPTERS = ["who", "money_rules", "projects", "temper", "love_language", "actions"]
ACTIONS = ["add", "update", "supersede"]
CLASSES = {"life": datetime.timedelta(days=14), "medication": datetime.timedelta(hours=24)}
REQUIRED = ["proposal_id", "schema", "created_at", "class", "subject", "confirmer",
            "source_id", "quote", "target", "action", "after", "status"]
ID_RE = re.compile(r"^p-\d{8}-\d{3,}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")

# 复用 v2.0 校验器的归一化+隐私正则（同目录 import；卡在文件名连字符上故显式处理）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import normalize, PRIVACY_PATTERNS  # noqa: E402

# ── 安全扫描：行为动词（指令伪装成事实——红队 T4 场结论）──
INSTR_PATTERNS = [
    ("定时/自动化指令",   re.compile(r"(以后|从今|从现在起|每天|每晚|每周|定时|自动)[^。]{0,12}(发送|发消息|群发|提醒|执行|发送给|通知)")),
    ("代发/代操作指令",   re.compile(r"(帮我|替我|给我|让AI|让助手|让他|让她)[^。]{0,8}(发|送|转|拨|买|删|改|执行|跑|下单|转账|汇款|付款)")),
    ("群发/全家广播",     re.compile(r"(群发|群聊发送|自动发送|定时发送|发给全家|通知全家|通知所有家人|全家群)")),
    ("档案写入指令",      re.compile(r"(档案|dossier)[^。]{0,6}(写入|加上|塞入|注入|改成|覆盖为)")),
    ("删除/覆盖档案",     re.compile(r"(删掉|删除|清除|抹掉|覆盖)[^。]{0,6}(档案|记录|条目|章节|dossier)")),
]
# ── 安全扫描：亲属词主语规则（对话主语错位——LLM 工程师 T1 场结论）──
# after 是档案事实陈述，出现亲属词=事实主体疑似第三方/错位；quote 是对话原话，天然含亲属词，不扫。
KINSHIP_RE = re.compile(
    r"(我|俺|他|她|老爷子|老太太)?(的)?(爸|妈|爸比|母亲|父亲|爷爷|奶奶|外公|外婆|姥姥|姥爷|"
    r"岳父|岳母|丈母娘|老丈人|婆婆|公公|儿媳|女婿|儿子|闺女|女儿|孙子|孙女|外孙|哥|姐|弟|妹|"
    r"兄弟|姐妹|侄|甥|叔叔|阿姨|伯|舅|姑|婶|姨)")
ANSI_RE = re.compile(r"\x1b(?:\[[0-9;]*[A-Za-z]|\][^\x07]*(?:\x07|\x1b\\)|[P^_][^\x1b]*\x1b\\)")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def strip_ansi(s):
    """终端转义序列+控制字符清洗（确认显示层防淹没问题，红队 T5 场结论）。"""
    return CONTROL_RE.sub("", ANSI_RE.sub("", s))


def sanitize_strings(obj):
    """递归 strip 所有字符串字段（submit 时落盘前清洗）。"""
    if isinstance(obj, dict):
        return {k: sanitize_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_strings(v) for v in obj]
    if isinstance(obj, str):
        return strip_ansi(obj)
    return obj


def parse_ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def expiry_of(p):
    return parse_ts(p["created_at"]) + CLASSES.get(p.get("class"), CLASSES["life"])


def is_expired(p, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        return parse_ts(p["created_at"]).astimezone(datetime.timezone.utc) < now and now > expiry_of(p).astimezone(datetime.timezone.utc)
    except Exception:
        return True  # 时间解析失败按过期处理，宁可拒绝不可放行


def scan_instruction(text):
    hits = []
    for name, pat in INSTR_PATTERNS:
        m = pat.search(text)
        if m:
            hits.append((name, f"…{m.group(0)[:20]}…"))
    return hits


def scan_kinship(text):
    m = KINSHIP_RE.search(text)
    return m.group(0) if m else None


def scan_privacy_text(text):
    n = normalize(text)
    for name, pat in PRIVACY_PATTERNS:
        m = pat.search(n)
        if m:
            return f"{name} → {m.group(0)[:4]}****"
    return None


# ═══════════════════ 闸② submit ═══════════════════

def validate_proposal(p, idx):
    """返回 (errors, security_hits)。errors→exit 1，security_hits→exit 2。"""
    errs, sec = [], []
    if not isinstance(p, dict):
        return [f"第{idx}行不是 JSON 对象"], []
    pid = p.get("proposal_id", f"<第{idx}行>")
    for k in REQUIRED:
        if k not in p:
            errs.append(f"{pid}: 缺少必填字段 {k}")
    if errs:
        return errs, sec
    if p["schema"] != SCHEMA_VERSION:
        errs.append(f"{pid}: schema 必须是 {SCHEMA_VERSION}（收到 {p['schema']}）")
    if not ID_RE.match(p["proposal_id"]):
        errs.append(f"{pid}: proposal_id 格式须为 p-YYYYMMDD-序号")
    if not TS_RE.match(p["created_at"]):
        errs.append(f"{pid}: created_at 必须是带显式时区的 ISO 8601（如 +08:00）——惰性生命周期依赖它")
    try:
        parse_ts(p["created_at"])
    except Exception:
        errs.append(f"{pid}: created_at 无法解析")
    if p.get("class") not in CLASSES:
        errs.append(f"{pid}: class 必须是 {'/'.join(CLASSES)}")
    if p.get("action") not in ACTIONS:
        errs.append(f"{pid}: action 必须是 {'/'.join(ACTIONS)}")
    if p.get("status") != "pending":
        errs.append(f"{pid}: submit 只接受 status=pending（收到 {p.get('status')}）——状态流转只能由本工具执行")
    if not isinstance(p.get("subject"), dict) or not all(k in p["subject"] for k in ("id", "alias", "relation")):
        errs.append(f"{pid}: subject 须含 id/alias/relation（主体分离铁律）")
    if not isinstance(p.get("confirmer"), dict) or not all(k in p["confirmer"] for k in ("id", "alias", "relation")):
        errs.append(f"{pid}: confirmer 须含 id/alias/relation（主体分离铁律）")
    t = p.get("target") or {}
    # 硬边界：基因层不进提案回路
    if t.get("layer") != "dossier":
        sec.append(f"{pid}: target.layer={t.get('layer')}——只有 dossier 层可提案；gene 层是慢变量，只走人工复访访谈（越权拒绝）")
    traversal = False
    for fld in ("section", "field"):
        v = t.get(fld)
        if isinstance(v, str) and re.search(r"[\\/.\x00]", v):
            sec.append(f"{pid}: target.{fld} 含路径字符——疑似路径穿越，拒绝")
            traversal = True
    if not traversal and t.get("section") not in CHAPTERS:
        errs.append(f"{pid}: target.section 必须是六章节之一，收到 {t.get('section')}")
    q = p.get("quote") or ""
    if not q.strip():
        errs.append(f"{pid}: quote（verbatim 引文）必填——提取契约 §1：after 必须能从 quote 推出")
    elif len(q) > 300:
        errs.append(f"{pid}: quote 超长（{len(q)}>300）")
    after = p.get("after") or ""
    if not after.strip():
        errs.append(f"{pid}: after 必填")
    elif len(after) > 500:
        errs.append(f"{pid}: after 超长（{len(after)}>500）")
    # 幻觉信号：LLM 自编引文——quote 与 after 相同
    if q.strip() and after.strip() and q.strip() == after.strip():
        sec.append(f"{pid}: quote 与 after 相同——疑似 LLM 自编引文（幻觉信号），拒收")
    if p.get("action") == "update" and not p.get("before"):
        errs.append(f"{pid}: action=update 必须带 before（确认人要看 diff）")
    # ── 安全扫描（闸②先行扫描，闸④入库前复验）──
    for field_name, val in (("after", after), ("before", p.get("before") or "")):
        if not val:
            continue
        for name, frag in scan_instruction(val):
            sec.append(f"{pid}: [{field_name}] 行为动词命中（{name}）→ {frag}——指令类内容禁止伪装成事实入库")
        if field_name == "after":
            kin = scan_kinship(val)
            if kin and not (p.get("third_party") or {}).get("anonymous_role"):
                sec.append(f"{pid}: after 出现亲属词「{kin}」且未声明 third_party——疑似主语错位或第三方信息；提取契约 §2：默认不提取，确需留存用匿名角色改写")
            ph = scan_privacy_text(val)
            if ph:
                sec.append(f"{pid}: after 隐私扫描命中（{ph}）")
    return errs, sec


def cmd_submit(args):
    try:
        with open(args.file, encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
    except Exception as e:
        print(f"[FAIL] 无法读取提案文件: {e}"); sys.exit(1)
    if not lines:
        print("[ok] 空提案包（零提取）——空输出是合法且被鼓励的输出"); sys.exit(0)
    errs_all, sec_all, clean = [], [], []
    for i, line in enumerate(lines, 1):
        try:
            p = json.loads(line)
        except Exception as e:
            errs_all.append(f"第{i}行 JSON 解析失败: {e}"); continue
        errs, sec = validate_proposal(p, i)
        errs_all += errs; sec_all += sec
        if not errs and not sec:
            clean.append(sanitize_strings(p))
    print(f"== 闸② 提案校验: {args.file}（{len(lines)} 行）==")
    for e in errs_all: print(f"  [结构] ✗ {e}")
    for s in sec_all: print(f"  [安全] ⛔ {s}")
    if errs_all:
        print("结果: 结构校验未通过，整包拒收 (exit 1)"); sys.exit(1)
    if sec_all:
        print("结果: 安全命中，整包拒收 (exit 2)——毒包不拆包，一处命中全包退回"); sys.exit(2)
    os.makedirs(args.dir, exist_ok=True)
    # 按周分片：proposals-YYYY-Www.jsonl
    shard = os.path.join(args.dir, f"proposals-{parse_ts(clean[0]['created_at']).strftime('%G-W%V')}.jsonl")
    with open(shard, "a", encoding="utf-8") as f:
        for p in clean:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"[ok] {len(clean)} 条提案落分片: {shard}")
    print("结果: 闸② 通过 ✅（下一步：dossier review 人工确认，勿在对话里追问用户）")
    sys.exit(0)


# ═══════════════════ 闸③ review / approve ═══════════════════

def load_shards(pdir):
    """返回 [(path, [records])]，按文件名排序。"""
    out = []
    if not os.path.isdir(pdir):
        return out
    for fn in sorted(os.listdir(pdir)):
        if fn.startswith("proposals-") and fn.endswith(".jsonl"):
            path = os.path.join(pdir, fn)
            with open(path, encoding="utf-8") as f:
                recs = [json.loads(l) for l in f.read().splitlines() if l.strip()]
            out.append((path, recs))
    return out


def save_shard(path, recs):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def lazy_expire(shards):
    """惰性过期：随读判定，禁后台定时器（维护者 T8 场结论）。返回过期列表。"""
    now = datetime.datetime.now(datetime.timezone.utc)
    expired = []
    for path, recs in shards:
        dirty = False
        for p in recs:
            if p.get("status") == "pending" and is_expired(p, now):
                p["status"] = "expired"
                p["expired_at"] = now.isoformat(timespec="seconds")
                dirty = True
                expired.append(p)
        if dirty:
            save_shard(path, recs)
    return expired


def risk_rank(p):
    """排序：矛盾冲突/第三方标记置顶 > class 紧急 > 时间旧者优先。confidence 不参与。"""
    r = 0
    if p.get("third_party"):
        r -= 2
    if p.get("class") == "medication":
        r -= 1
    if p.get("action") == "supersede":
        r -= 1
    try:
        return (r, p["created_at"])
    except Exception:
        return (r, "")


def cmd_review(args):
    shards = load_shards(args.dir)
    expired = lazy_expire(shards)
    pending = sorted([p for _, recs in shards for p in recs if p.get("status") == "pending"], key=risk_rank)
    print(f"== 闸③ 提案待确认（{len(pending)} 条 pending）==")
    # 冻结转摘要：过期不销毁，转"两周回顾"清单
    if expired:
        print(f"\n[冻结摘要] {len(expired)} 条提案已过期冻结（未销毁，等你勾选）：")
        for p in expired:
            print(f"  · {p['proposal_id']} [{p.get('class')}] {strip_ansi(p['after'])[:40]}…")
        print("  （如仍想入库，请让 AI 重新提取生成新提案；原提案保留留痕）")
    if not pending:
        print("\n当前无待确认提案 ✅")
        sys.exit(0)
    print("\n[摘要先行]（按风险排序：第三方/用药/替代置顶；confidence 不参与排序）")
    for p in pending:
        tp = " ⚠️涉第三方未告知" if p.get("third_party") and not p["third_party"].get("disclosed") else ""
        med = " 💊用药类24h" if p.get("class") == "medication" else ""
        sup = " 🔁替代既有条目" if p.get("action") == "supersede" else ""
        print(f"  {p['proposal_id']} [{p['target']['section']}/{p['action']}]{med}{tp}{sup}")
        print(f"      事由: {strip_ansi(p['after'])[:60]}{'…' if len(p['after']) > 60 else ''}")
    if not args.summary:
        print("\n[明细 diff]")
        for p in pending:
            before = strip_ansi(p.get("before") or "（新增）")
            print(f"  ── {p['proposal_id']} ──")
            print(f"     引文: 「{strip_ansi(p['quote'])[:80]}」")
            print(f"     - 旧: {before[:100]}")
            print(f"     + 新: {strip_ansi(p['after'])[:100]}")
            print(f"     主体: {p['subject']['alias']}({p['subject']['relation']})  确认人: {p['confirmer']['alias']}({p['confirmer']['relation']})")
    print(f"\n批准: python proposal.py approve --dir {args.dir} --ids <id1,id2>   （单批≤5；一次批≥3 需追加 --confirm-batch）")
    sys.exit(0)


def cmd_approve(args):
    ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    if not ids:
        print("[FAIL] --ids 为空"); sys.exit(4)
    if len(ids) > 5:
        print(f"[FAIL] 单批 {len(ids)} 条 > 上限 5 条——分批纪律：不堆积、不绑架确认人"); sys.exit(4)
    if len(ids) >= 3 and not args.confirm_batch:
        print(f"[FAIL] 一次批准 {len(ids)} 条 ≥3——连批疲劳是攻击面（红队结论），请追加 --confirm-batch 二次确认"); sys.exit(4)
    shards = load_shards(args.dir)
    expired = lazy_expire(shards)
    expired_ids = {p["proposal_id"] for p in expired}
    for pid in ids:
        if pid in expired_ids:
            print(f"[FAIL] {pid} 已过期冻结（惰性判定）——过期不批，如仍需要请重新提取 (exit 5)"); sys.exit(5)
    found = {}
    for path, recs in shards:
        for p in recs:
            if p["proposal_id"] in ids:
                found[p["proposal_id"]] = (path, p)
    missing = [i for i in ids if i not in found]
    if missing:
        print(f"[FAIL] 未找到提案: {','.join(missing)}"); sys.exit(4)
    bad = [(pid, p) for pid, (path, p) in found.items() if p.get("status") != "pending"]
    for pid, p in bad:
        if p.get("status") == "expired":
            print(f"[FAIL] {pid} 已过期冻结（惰性判定）——过期不批，如仍需要请重新提取 (exit 5)"); sys.exit(5)
        print(f"[FAIL] {pid} 状态为 {p.get('status')}，非 pending，不可批准"); sys.exit(4)
    for pid, (path, p) in found.items():
        p["status"] = "approved"
        p["approved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    for path, recs in shards:
        if any(p.get("status") == "approved" for p in recs):
            save_shard(path, recs)
    print(f"[ok] 已批准 {len(found)} 条: {','.join(found)}")
    print("下一步: python proposal.py ingest --dossier <dossier.json> --dir %s --cardgen scripts/card-gen.py" % args.dir)
    sys.exit(0)


# ═══════════════════ 闸④⑤ ingest ═══════════════════

def compute_digest(d):
    """与 card-gen.py 同算法：去除 tokens.integrity 后的 sha256。"""
    clone = json.loads(json.dumps(d, ensure_ascii=False))
    clone.get("tokens", {}).pop("integrity", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def scrub_env():
    """card-gen 子进程环境白名单（红队 T6 场：防被污染环境变量进入派生链）。"""
    keep = ["SYSTEMROOT", "SYSTEMDRIVE", "COMSPEC", "PATHEXT", "PATH", "TMP", "TEMP", "PYTHONIOENCODING"]
    return {k: os.environ[k] for k in keep if k in os.environ}


def cmd_ingest(args):
    shards = load_shards(args.dir)
    approved = [(path, p) for path, recs in shards for p in recs if p.get("status") == "approved"]
    print(f"== 闸④⑤ 入库: {len(approved)} 条 approved ==")
    if not approved:
        print("[ok] 无待入库提案"); sys.exit(0)
    with open(args.dossier, encoding="utf-8") as f:
        d = json.load(f)
    # ⑤-1 完整性前置校验：档案签发后被篡改即全部中止（宁可全停，不部分入库）
    stored = (d.get("tokens", {}).get("integrity", {}) or {}).get("digest")
    if stored:
        actual = compute_digest(d)
        if stored != actual:
            print("[FAIL] 完整性校验失败：档案在签发后被人工篡改——拒绝入库。改动合法请先重跑 card-gen.py 重新签发 (exit 3)")
            sys.exit(3)
    ingested, rescanned = [], []
    for path, p in approved:
        pid = p["proposal_id"]
        # 闸④ 复验（确认不豁免扫描——确认人批准≠扫描放行）
        hits = []
        for val in (p.get("after") or "", p.get("before") or ""):
            if not val:
                continue
            for name, frag in scan_instruction(val):
                hits.append(f"行为动词({name}) → {frag}")
            ph = scan_privacy_text(val)
            if ph:
                hits.append(f"隐私命中 {ph}")
        kin = scan_kinship(p.get("after") or "")
        if kin and not (p.get("third_party") or {}).get("anonymous_role"):
            hits.append(f"亲属词主语规则「{kin}」")
        if hits:
            p["status"] = "rejected_scan"
            p["rejected_reason"] = "；".join(hits)
            rescanned.append((pid, hits, path))
            continue
        # ⑤-2 timeline 追加式写入（不覆盖章节内容本身，变更史全留痕）
        d.setdefault("timeline", []).append({
            "proposal_id": pid,
            "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "observed_at": p["created_at"],
            "source_id": p["source_id"],
            "subject": p["subject"]["id"],
            "confirmer": p["confirmer"]["id"],
            "action": p["action"],
            "target": p["target"],
            "before": p.get("before"),
            "after": p["after"],
            "class": p.get("class"),
            "third_party": p.get("third_party"),
        })
        p["status"] = "ingested"
        ingested.append((pid, path))
    # 状态写回分片（记录对象已原地改状态，整体重写各分片）
    for path, recs in shards:
        save_shard(path, recs)
    if rescanned:
        print("结果: 闸④ 扫描复验命中，命中提案拒绝入库 (exit 2)：")
        for pid, hits, path in rescanned:
            print(f"  ⛔ {pid}: {'；'.join(hits)}（状态已标 rejected_scan，留痕不销毁）")
        sys.exit(2)
    # ⑤-3 写回档案 + 重新签发完整性校验和 + card 重派生
    #（ingest 是被授权的写入方：入库前已验证签发后无越手篡改，入库内容合法变更后由本工具重签）
    d["meta"]["updated"] = datetime.datetime.now().strftime("%Y-%m-%d")
    d.setdefault("tokens", {})["integrity"] = {"algorithm": "sha256", "digest": compute_digest(d)}
    with open(args.dossier, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"[ok] timeline 追加 {len(ingested)} 条 → {args.dossier}")
    cardgen_note = "未执行（未提供 --cardgen）"
    if args.cardgen:
        cardgen = os.path.abspath(args.cardgen)
        if os.path.basename(cardgen) != "card-gen.py" or not os.path.exists(cardgen):
            print(f"[FAIL] --cardgen 白名单失败: 只允许 card-gen.py 且路径须存在（收到 {args.cardgen}）"); sys.exit(1)
        r = subprocess.run([sys.executable, cardgen, os.path.abspath(args.dossier)],
                           env=scrub_env(), capture_output=True, text=True, encoding="utf-8", errors="replace")
        cardgen_note = f"exit {r.returncode}"
        print(f"[ok] card-gen 重派生: exit {r.returncode}")
        if r.returncode != 0:
            print(r.stdout or ""); print(r.stderr or "")
            print("结果: card 重派生失败，timeline 已写入但派生链断裂——修复后重跑 card-gen.py (exit 3)")
            sys.exit(3)
    # ⑤-4 输入清单哈希（可复现性：本批 ingest 吃了哪些文件、什么状态）
    manifest = {
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "ingested": [pid for pid, _ in ingested],
        "inputs": {
            "dossier": file_sha256(os.path.abspath(args.dossier)),
            **{os.path.basename(path): file_sha256(path) for path, _ in shards},
        },
    }
    outdir = os.path.join(os.path.dirname(os.path.abspath(args.dossier)), "derived")
    os.makedirs(outdir, exist_ok=True)
    mpath = os.path.join(outdir, "ingest-manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[ok] 输入清单哈希: {mpath}")
    print(f"[info] cardgen: {cardgen_note}")
    print("结果: 闸④⑤ 通过，入库完成 ✅")
    sys.exit(0)


# ═══════════════════ lifecycle 自检 ═══════════════════

def cmd_lifecycle(args):
    shards = load_shards(args.dir)
    counts = {}
    expired_now = lazy_expire(shards)
    for _, recs in shards:
        for p in recs:
            counts[p.get("status", "?")] = counts.get(p.get("status", "?"), 0) + 1
    print("== 提案生命周期自检（惰性判定，本次读取时触发）==")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    if expired_now:
        print(f"[冻结摘要] 本次判定过期 {len(expired_now)} 条（已冻结转摘要，未销毁）")
    print("结果: 自检完成 ✅（无后台定时器——一切过期判定只发生在读取时）")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="知心档案 · v2.6 档案更新回路（闸②③④⑤）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("submit", help="闸②：提案校验+落分片（LLM 零写入）")
    s.add_argument("file"); s.add_argument("--dir", required=True)
    s.set_defaults(func=cmd_submit)
    r = sub.add_parser("review", help="闸③：惰性过期+摘要先行+diff 展示")
    r.add_argument("--dir", required=True)
    r.add_argument("--summary", action="store_true", help="只看摘要，不展开 diff")
    r.set_defaults(func=cmd_review)
    a = sub.add_parser("approve", help="闸③：批准（≤5 条；≥3 需 --confirm-batch）")
    a.add_argument("--dir", required=True)
    a.add_argument("--ids", required=True)
    a.add_argument("--confirm-batch", action="store_true")
    a.set_defaults(func=cmd_approve)
    i = sub.add_parser("ingest", help="闸④⑤：扫描复验→timeline→重派生→清单哈希")
    i.add_argument("--dossier", required=True)
    i.add_argument("--dir", required=True)
    i.add_argument("--cardgen", default=None, help="card-gen.py 路径（白名单：只接受该文件名）")
    i.set_defaults(func=cmd_ingest)
    lc = sub.add_parser("lifecycle", help="生命周期自检（惰性判定）")
    lc.add_argument("--dir", required=True)
    lc.set_defaults(func=cmd_lifecycle)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
