# Roadmap

> AWS Lambda MicroVM Lab Development Roadmap

このドキュメントでは AWS Lambda MicroVM Lab の開発ロードマップを管理します。

各STEPは独立して動作するサンプルとして実装し、徐々に AI Developer Workspace を構築していきます。

---

# Goal

最終目標

> **AWS Lambda MicroVM を利用した数秒で起動できる AI Development Workspace**

構築する要素

- Browser Terminal
- Linux Desktop
- Browser Automation
- Desktop Automation
- Cloud IDE
- AI Coding Agent
- Persistent Workspace
- Multi Agent Environment

---

# Phase 1

## Environment Foundation

MicroVMを利用したLinux実行環境を構築する。

---

## STEP1 Hello MicroVM

### Goal

最小構成で MicroVM を起動する。

### Learn

- Image作成
- Dockerfile
- Lambda MicroVM
- 起動方法

### Deliverables

- Hello World

Status

✅ Completed

---

## STEP2 Web Terminal

### Goal

ブラウザからTerminalへ接続する。

### Learn

- ttyd
- WebSocket
- Terminal公開
- Proxy

### Deliverables

```
Browser

↓

Terminal
```

Status

✅ Completed

---

## STEP3 Linux Desktop

### Goal

GUIを表示する。

### Learn

- Xvfb
- TigerVNC
- noVNC

### Deliverables

```
Browser

↓

Linux Desktop
```

Status

✅ Completed

---

## STEP4 Desktop Survey

### Goal

Amazon Linux上で利用可能なDesktop環境を調査する。

調査対象

- Openbox
- Fluxbox
- IceWM
- XFCE
- LXDE

### Deliverables

利用可能Desktop一覧

Status

✅ Completed

---

## STEP5 Firefox Desktop

### Goal

GUIアプリケーションを動かす。

### Learn

- Firefox
- 日本語フォント
- Locale
- Timezone

### Deliverables

Firefox Desktop

Status

✅ Completed

---

# Phase 2

## Browser Automation

---

## STEP6 Playwright

### Goal

ブラウザ自動操作

### Learn

- Playwright
- Browser Automation
- Screenshot
- GUI Debug

### Deliverables

- Firefox自動起動
- 自動ページ遷移
- Screenshot取得

Status

✅ Completed

---

# Phase 3

## Desktop Automation

---

## STEP7 Desktop Automation

### Goal

Linux Desktop全体を自動操作する。

### Learn

当初予定していた xdotool / wmctrl / xclip / OCR は Amazon Linux 2023 標準リポジトリに存在しないため、実装では Desktop の**状態観測**に着地した。

- xwininfo（ウィンドウ一覧）
- xrandr（解像度）
- xlsclients（接続クライアント）
- ImageMagick（スクリーンショット）

### Deliverables

- ウィンドウ一覧・解像度・スクリーンショットを `desktop-state.json` に保存
- Mouse Move / Click / Keyboard / Clipboard / OCR による実操作は STEP10 以降へ持ち越し

Status

✅ Completed（状態観測のみ。実操作はSTEP10/11で継続）

---

# Phase 4

## Cloud IDE

---

## STEP8 code-server

### Goal

ブラウザだけでVS Codeを利用する。

### Learn

- code-server
- Git
- GitHub CLI

### Deliverables

```
Browser

↓

VS Code
```

Status

✅ Completed

---

# Phase 5

## AI Coding

---

## STEP9 Claude Code

### Goal

MicroVM上で Claude Code を実行する。

### Learn

- Claude Code
- Terminal
- Git
- Build

### Deliverables

AI Coding Environment

Status

✅ Completed

---

# Phase 6

## Desktop Agent

---

## STEP10 AI Desktop Agent

### Goal

Desktop全体をAIが操作する。

### Learn

- Desktop Automation
- Vision
- OCR
- Tool Use

### Deliverables

```
AI

↓

Desktop

↓

VS Code

Firefox

Terminal
```

例

```
README読む

↓

コード修正

↓

Build

↓

Test

↓

Commit
```

### 現状

- `desktop_observer.py`: ウィンドウ一覧・解像度・スクリーンショット取得は実装済み
- `desktop_controller.py`: move_mouse / click / type_text / keypress / focus_window のインターフェースのみ実装。実操作は `status: "not_implemented"`（xdotool未導入のため）

Status

🚧 In Progress（観測は完了、実操作は未実装）

---

# Phase 7

## Desktop Tools

---

## STEP11 Desktop Tools

### Goal

STEP10 の observer / controller を再利用可能な `desktop` パッケージにまとめ、Claude Code や将来のAgentから呼び出せる統一APIを提供する。

### Learn

- Pythonパッケージ設計（`desktop/__init__.py`, `observer.py`, `controller.py`, `planner.py`, `tools.py`）
- アクションキューイングの設計

### Deliverables

- `desktop.observer`: Desktop状態・スクリーンショット取得
- `desktop.controller`: アクションを `desktop-actions.json` にキューイング（`status: "queued"`。実行はまだ未実装）
- `desktop.planner`: 指示文からアクションプランを生成する骨組み（実プランニングロジックは未実装）
- `desktop.tools.DesktopTools`: 上記をまとめた統一API

Status

🚧 In Progress

---

# Phase 8

## Persistent Workspace

---

## STEP12 Persistent Workspace

### Goal

MicroVM停止後も作業内容を保持する。

候補

- GitHub
- S3
- EFS

### Deliverables

Resume可能Workspace

Status

⏳ Planned

---

# Phase 9

## Multi Agent

---

## STEP13 Multi Agent

### Goal

複数MicroVMを利用する。

例

```
Agent A

↓

Frontend

────────────

Agent B

↓

Backend

────────────

Agent C

↓

Testing
```

### Deliverables

AI Team Development

Status

⏳ Planned

---

# Long Term Vision

```
Browser

↓

Proxy

↓

Lambda MicroVM

↓

Linux Desktop

↓

VS Code

↓

Claude Code

↓

Desktop Agent

↓

Persistent Workspace

↓

Multi Agent
```

---

# Ideas

将来的に検証したい内容

- Claude Desktop
- Gemini CLI
- Codex CLI
- Continue.dev
- OpenHands
- Browser Use
- Computer Use
- MCP Server
- VS Code Extension
- GitHub Actions
- Snapshot
- Resume
- Session Sharing
- Remote Pair Programming

---

# Design Principles

- STEPごとに独立したサンプルとする
- 共通処理は `scripts/` と `common/` に集約する
- 起動方法は `./scripts/run.sh stepX` に統一する
- ドキュメントを実装と同時に更新する
- DesktopとAI Agentを中心に発展させる

---

# Success Criteria

最終的に実現したいこと

- ブラウザだけで開発環境を起動できる
- AIがDesktop全体を操作できる
- 数秒でWorkspaceを起動できる
- GitHubからCloneしてすぐ開発できる
- MicroVMをAI Developer Workspaceとして利用できる



