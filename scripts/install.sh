#!/usr/bin/env bash
# 知心档案 · 一键安装（macOS / Linux / Git Bash）
# 自动探测安装目标：Claude Code (~/.claude/skills) / DSH NEXT (~/.dsh/skills)
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"

install_to() {
  local dest="$1" label="$2"
  if [ ! -d "$dest" ]; then
    echo "[skip] 未找到 $label（$dest）"
    return
  fi
  mkdir -p "$dest/dossier"
  cp "$SRC/skill/SKILL.md" "$dest/dossier/SKILL.md"
  mkdir -p "$dest/dossier/assets"
  cp "$SRC/schema/dossier.schema.json" "$dest/dossier/assets/"
  cp -r "$SRC/templates" "$dest/dossier/assets/templates"
  cp "$SRC/scripts/validate.py" "$dest/dossier/assets/"
  echo "[ok] 已安装到 $label: $dest/dossier/"
}

echo "== 知心档案安装器 =="
install_to "$HOME/.claude/skills" "Claude Code"
install_to "$HOME/.dsh/skills" "DSH NEXT"
echo "完成。在你的 Agent 里说「用知心档案给XX建一份档案」即可开始。"
echo "（手动安装：把 skill/SKILL.md + schema + templates 复制到你 Agent 的技能目录）"
