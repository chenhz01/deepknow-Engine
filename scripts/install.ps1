# zhixin-dossier installer (Windows PowerShell 5.1+ compatible, ASCII only)
# Auto-detects targets: Claude Code (~/.claude/skills) / DSH NEXT (~/.dsh/skills)
$ErrorActionPreference = "Stop"
$Src = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Install-To($Dest, $Label) {
    if (-not (Test-Path $Dest)) {
        Write-Output "[skip] $Label not found ($Dest)"
        return
    }
    $Target = Join-Path $Dest "dossier"
    New-Item -ItemType Directory -Force -Path (Join-Path $Target "assets") | Out-Null
    Copy-Item (Join-Path $Src "skill\SKILL.md") (Join-Path $Target "SKILL.md") -Force
    Copy-Item (Join-Path $Src "schema\dossier.schema.json") (Join-Path $Target "assets\") -Force
    Copy-Item (Join-Path $Src "templates") (Join-Path $Target "assets\templates") -Recurse -Force
    Copy-Item (Join-Path $Src "scripts\validate.py") (Join-Path $Target "assets\") -Force
    Write-Output "[ok] installed to ${Label}: $Target"
}

Write-Output "== zhixin-dossier installer =="
Install-To (Join-Path $HOME ".claude\skills") "Claude Code"
Install-To (Join-Path $HOME ".dsh\skills") "DSH NEXT"
Write-Output "Done. Say this to your agent: 'build a dossier for <someone>'"
