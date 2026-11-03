#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zhixin-dossier v2.5 对话引头引擎（Dialogue Hooks Engine）
=========================================================
脑暴三方共识的落地（详 docs/dialogue-hooks.md）：
1. 引擎算条件、LLM 只管说话（prompt工程师+信息架构师共识）——
   时间/计数/冷却/配额全部本地确定性执行，LLM 只消费 fired 结果负责表达。
2. 默认永不主动（伦理+用户共识）——proactivity.level=0 时本引擎零输出。
3. 注入防护（红队共识）——话术黑名单扫描+白名单占位符，违规整包拒绝装载。
4. 每轮只出口 1 条（游戏机制共识）——配额/冷却/静音时段/疲劳计数/优先级仲裁。

用法：
  python hooks_engine.py --hooks pack.json --state state.json \
      --level 2 --time "2026-11-04T23:10" --last-user "还在赶方案" --turns 5
输出：stdout JSON（fired 结果或 fired: null）；状态增量回写 state 文件。
退出码：0 正常（含 fired:null）｜2 包不安全拒绝装载｜3 参数错误
"""
import argparse, json, re, sys, hashlib
from datetime import datetime, timedelta

# ---------- 红队共识：话术安全 ---------- #
PLACEHOLDER_WHITELIST = {"name", "nickname"}  # 仅允许称谓类占位符
OPENER_MAXLEN = 120
# 黑名单：URL/联系方式/金额/账号/指令注入式祈使（加载时命中即拒绝整包）
BLACKLIST = [
    r"https?://", r"\b\d{7,}\b",                       # 链接、长数字（账号/电话）
    r"(转账|汇款|打款|付款|收款)[到给]",                 # 资金引导
    r"(忽略|无视|忘掉)(之前|前面|上述|前述)",            # 指令注入
    r"(发送|发到|私信|加我)",                            # 导流行为
    r"\b(password|密码|验证码)\b",
]
def phrase_is_safe(text: str) -> bool:
    if len(text) > OPENER_MAXLEN:
        return False
    for pat in BLACKLIST:
        if re.search(pat, text):
            return False
    return True

def placeholders_ok(text: str) -> bool:
    for name in re.findall(r"\{(\w+)\}", text):
        if name not in PLACEHOLDER_WHITELIST:
            return False
    return True

def load_pack(path):
    """装载并安全校验：黑名单命中=拒绝整包（exit 2）"""
    with open(path, encoding="utf-8") as f:
        pack = json.load(f)
    for hook in pack.get("hooks", []):
        resp = hook.get("response", {})
        phrases = resp.get("openers", [])
        for j in resp.get("judgments", []):
            phrases.append(j.get("then_say", ""))
        th = resp.get("thread", {})
        phrases += th.get("openers", [])
        for p in phrases:
            if not phrase_is_safe(p) or not placeholders_ok(p):
                print(json.dumps({"error": "unsafe_phrase", "hook": hook.get("id"),
                                  "phrase": p[:60]}, ensure_ascii=False))
                sys.exit(2)
    return pack

# ---------- 时机评分（认知科学共识，简化可判定版） ---------- #
def timing_score(hook, last_user, valence_now, days_since_echo):
    """0.5*话题重叠 + 0.3*效价匹配 + 0.2*间隔分；>0.65 才许主动开口"""
    kws = hook.get("condition", {}).get("keyword", {})
    tags = kws.get("patterns", []) + kws.get("topic_tags", [])
    overlap = 1.0 if any(t and t in (last_user or "") for t in tags) else 0.0
    vmatch = 1.0 if (valence_now >= 0) == (hook.get("valence", 0) >= 0) else 0.0
    gap = min(1.0, max(0.0, (days_since_echo or 0) / 14.0)) if hook.get("valence", 0) < 0 else 1.0
    return 0.5 * overlap + 0.3 * vmatch + 0.2 * gap

# ---------- 条件评估（引擎硬闸，确定性） ---------- #
def in_time_window(now, window):
    start, end = window.get("start", "00:00"), window.get("end", "23:59")
    days = window.get("days")
    if days is not None and now.weekday() not in days:
        return False
    t = now.strftime("%H:%M")
    return start <= t <= end if start <= end else (t >= start or t <= end)

def cond_ok(cond, now, last_user, state):
    kind = cond.get("kind")
    if kind == "time_window":
        return in_time_window(now, cond.get("window", {}))
    if kind == "keyword":
        kws = cond.get("keyword", {})
        for pat in kws.get("patterns", []):
            if kws.get("mode") == "regex":
                if re.search(pat, last_user or ""): return True
            elif pat and pat in (last_user or ""): return True
        return False
    if kind == "counter":
        c = cond["counter"]
        val = state.get("counters", {}).get(c["key"], 0)
        return {"gte": val >= c["threshold"], "lte": val <= c["threshold"],
                "eq": val == c["threshold"]}[c["op"]]
    if kind == "event":
        ev = cond.get("event", {})
        if ev["name"] == "thread_due":
            th = state.get("threads", {}).get(ev["params"].get("thread_id"), {})
            return th.get("status") == "open"
        if ev["name"] == "user_absent_days":
            last = state.get("last_seen")
            if not last: return False
            delta = (now - datetime.fromisoformat(last)).days
            return delta >= ev["params"].get("days", 3)
        return False
    if kind == "allOf":
        return all(cond_ok(c, now, last_user, state) for c in cond.get("allOf", []))
    return False

# ---------- 情节引线状态机（剧作家共识） ---------- #
def plotline_due(thread, now, state):
    if thread.get("passive_only") or thread.get("status") != "open":
        return False
    if thread.get("echo_count", 0) >= 2:          # 回收预算=2
        return False
    last = thread.get("last_echo_at")
    if last:
        gap = now - datetime.fromisoformat(last)
        if gap < timedelta(days=7):               # 间隔>=7天
            return False
        if gap > timedelta(days=90):              # 90天无人提及→封存
            thread["status"] = "archived"
            return False
    return True

# ---------- 主评估 ---------- #
def evaluate(pack, level, now, last_user, turns, state):
    pro = pack.get("proactivity", {})
    cap = pro.get("daily_cap", 3)
    today = now.strftime("%Y-%m-%d")
    if state.get("count_date") != today:
        state["count_date"], state["fired_today"] = today, 0
    fired_today = state.get("fired_today", 0)
    result = {"fired": None, "quota_left": max(0, cap - fired_today),
              "level": level, "skipped": []}
    # 总闸：L0 或超额 → 全静默（伦理共识：默认关闭，宁可沉默不可猜错）
    if level <= 0 or fired_today >= cap:
        result["skipped"].append("proactivity_gate" if level <= 0 else "daily_cap")
        return result
    # 全局冷却 + 静音时段
    gc = state.get("last_fired_at")
    if gc and (now - datetime.fromisoformat(gc)) < timedelta(minutes=pro.get("global_cooldown_min", 120)):
        result["skipped"].append("global_cooldown"); return result
    quiet = pro.get("quiet_hours", [])
    is_quiet = len(quiet) == 2 and not in_time_window(now, {"start": quiet[1], "end": quiet[0]})
    # 候选筛选：passive_only 永不主动；配额内逐条硬闸
    candidates = []
    for h in pack.get("hooks", []):
        hid = h.get("id", "?")
        if h.get("passive_only"):
            result["skipped"].append(f"{hid}:passive_only"); continue
        if h.get("valence", 0) < 0:
            result["skipped"].append(f"{hid}:negative_valence_no_proactive"); continue
        if is_quiet and not (h.get("channel") == "care" and h.get("risk_level", 0) <= 1):
            result["skipped"].append(f"{hid}:quiet_hours"); continue
        if h.get("channel") == "care" and level < 1:
            result["skipped"].append(f"{hid}:level_low"); continue
        if h.get("channel") in ("chat", "task") and level < 2:
            result["skipped"].append(f"{hid}:level_low"); continue
        # 疲劳计数（新鲜感共识）：used>=3 降权停用
        fkey = f"fatigue:{hid}"
        if state.get("counters", {}).get(fkey, 0) >= 3:
            result["skipped"].append(f"{hid}:fatigue"); continue
        # 每钩冷却
        lf = state.get("hook_last_fired", {}).get(hid)
        if lf and (now - datetime.fromisoformat(lf)) < timedelta(minutes=h.get("cooldown_min", 0)):
            result["skipped"].append(f"{hid}:cooldown"); continue
        # 类型评估
        htype, resp = h["type"], h["response"]
        if htype == "trigger":
            if not cond_ok(h["condition"], now, last_user, state):
                continue
            score = timing_score(h, last_user, 0, None)
            if h["condition"].get("kind") == "keyword" and score < 0.65:
                result["skipped"].append(f"{hid}:timing_{score:.2f}"); continue
            candidates.append((h["priority"], hid, "trigger", resp, h))
        elif htype == "plotline":
            th = resp.get("thread", {})
            threads = state.setdefault("threads", {})
            live = threads.setdefault(th["id"], {**th, "echo_count": th.get("echo_count", 0),
                                                 "status": th.get("status", "open"),
                                                 "last_echo_at": th.get("last_echo_at")})
            if plotline_due(live, now, state):
                candidates.append((h["priority"], hid, "plotline", resp, h))
        elif htype == "logic":
            if cond_ok(h["condition"], now, last_user, state):
                candidates.append((h["priority"], hid, "logic", resp, h))
    if not candidates:
        return result
    # 仲裁：同轮仅出口 1 条（priority 最小者）；其余按 suppress 抑制
    candidates.sort(key=lambda x: (x[0], x[1]))
    prio, hid, htype, resp, h = candidates[0]
    rendered = None
    if htype == "trigger":
        pool = resp.get("openers", [])
        used = state.setdefault("opener_used", {})
        order = sorted(range(len(pool)), key=lambda i: used.get(f"{hid}:{i}", ""))
        rendered = pool[order[0]]
        used[f"{hid}:{order[0]}"] = now.isoformat()
    elif htype == "plotline":
        th = resp["thread"]; live = state["threads"][th["id"]]
        pool = th.get("openers", ["({name}) 上次说的事，后来怎么样了？"])
        rendered = pool[min(live["echo_count"], len(pool) - 1)]
        live["echo_count"] += 1
        live["last_echo_at"] = now.isoformat()
        if live["echo_count"] >= 2:
            live["status"] = "cooling"   # 回收预算用尽→冷却30天（剧作家共识）
    elif htype == "logic":
        rendered = {"_logic": resp["judgments"]}  # LLM 层消费 if/then，不直接出口
        rendered = resp["judgments"][0]["then_say"]
    # 安全渲染：占位符替换（红队：字段值包数据边界）
    persona = state.get("persona", {})
    if isinstance(rendered, str):
        rendered = rendered.replace("{name}", persona.get("name") or "你")
        rendered = rendered.replace("{nickname}", persona.get("nickname") or "你")
        rendered = re.sub(r"(?<=[，。！？,,])\s*[，,]+", "", rendered)  # 占位符空值兜底后清双标点
    # 状态回写
    state["fired_today"] = fired_today + 1
    state.setdefault("hook_last_fired", {})[hid] = now.isoformat()
    state["last_fired_at"] = now.isoformat()
    fk = f"fatigue:{hid}"
    state.setdefault("counters", {})[fk] = state.get("counters", {}).get(fk, 0) + 1
    # 触发日志（律师共识：最小化——记事件与规则 id，不记行为轨迹）
    state.setdefault("audit_log", []).append({
        "at_date": today, "hook": hid, "channel": h.get("channel"), "type": htype})
    result["fired"] = {"hook": hid, "type": htype, "speak_as": h.get("speak_as", "self"),
                       "channel": h.get("channel"), "say": rendered,
                       "note": "LLM 层请以 speak_as 名义自然说出，禁解释触发机制（红队 3a 自解释仅在用户追问时按 audit_log 答复）"}
    result["quota_left"] = max(0, cap - state["fired_today"])
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hooks", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--time", default=None)
    ap.add_argument("--last-user", default="")
    ap.add_argument("--turns", type=int, default=0)
    a = ap.parse_args()
    pack = load_pack(a.hooks)
    now = datetime.fromisoformat(a.time) if a.time else datetime.now()
    try:
        state = json.load(open(a.state, encoding="utf-8"))
    except FileNotFoundError:
        state = {}
    result = evaluate(pack, a.level, now, a.last_user, a.turns, state)
    with open(a.state, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
