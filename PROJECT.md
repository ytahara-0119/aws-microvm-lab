# PROJECT

> AWS Lambda MicroVM Lab 開発プロジェクト

このドキュメントは現在の開発状況と今後の予定を管理するためのドキュメントです。

---

# Project Goal

AWS Lambda MicroVM を利用して、

- Browser Terminal
- Linux Desktop
- Browser Automation
- Desktop Automation
- Cloud IDE
- AI Coding Agent
- AI Development Workspace

を段階的に構築する。

最終目標は

> **数秒で起動できる AI Developer Workspace**

を実現すること。

---

# Current Status

## Current Step

> **STEP11 Desktop Tools**

STEP9 Claude Code までで、MicroVM上で code-server + Claude Code + Git を利用できる開発環境が完成。

STEP10 AI Desktop Agent で Desktop の状態観測（ウィンドウ一覧・解像度・スクリーンショット）を実装し、STEP11 Desktop Tools でその機能を `desktop` パッケージ（observer / controller / planner / tools）として再構成中。

現時点ではマウス移動・クリック・キー入力などの実操作は `xdotool` が Amazon Linux 2023 標準リポジトリに存在しないため未実装で、`desktop.controller` はアクションをキューに積むところまでの実装（`status: "queued"`）。

---

# Progress

| Step | Description | Status |
|-------|-------------|--------|
| STEP1 | Hello MicroVM | ✅ |
| STEP2 | Web Terminal | ✅ |
| STEP3 | noVNC Desktop | ✅ |
| STEP4 | Desktop Survey | ✅ |
| STEP5 | Firefox Desktop | ✅ |
| STEP6 | Playwright Browser Automation | ✅ |
| STEP7 | Desktop Automation（状態観測） | ✅ |
| STEP8 | code-server | ✅ |
| STEP9 | Claude Code | ✅ |
| STEP10 | AI Desktop Agent（観測のみ、操作は未実装） | 🚧 |
| STEP11 | Desktop Tools（observer/controller/planner/tools 化） | 🚧 |
| STEP12 | Persistent Workspace | ⏳ |
| STEP13 | Multi Agent | ⏳ |

※ 当初ロードマップの STEP11「Persistent Workspace」は、実際の開発では「Desktop Tools」の実装が優先され、Persistent Workspace / Multi Agent は STEP12 / STEP13 に繰り下げ。

---

# Completed Features

## Common

- 共通起動スクリプト
- 共通 Proxy
- 共通 MicroVM Launcher

```
./scripts/run.sh stepX
```

---

## Terminal

- ttyd

```
Browser

↓

Terminal
```

---

## Desktop

- Xvfb
- TigerVNC
- noVNC

```
Browser

↓

Desktop
```

---

## Browser

- Firefox
- 日本語フォント
- 日本語ロケール
- Asia/Tokyo

---

## Playwright（STEP6）

- Firefox自動起動
- ページ遷移
- スクリーンショット
- GUI確認

---

## Desktop Automation（STEP7）

計画では xdotool / wmctrl / xclip / OCR を予定していたが、実装では以下の Desktop 状態観測に着地。

- `xwininfo` によるウィンドウ一覧取得
- `xrandr` による解像度取得
- `xlsclients` による接続クライアント一覧
- ImageMagick(`import`) によるスクリーンショット取得
- 取得結果を `desktop-state.json` に保存

---

## code-server（STEP8）

- code-server インストール・起動
- パスワード認証設定
- VS Code設定ファイルの自動生成

```
Browser

↓

code-server

↓

VS Code
```

---

## Claude Code（STEP9）

- Node.js / npm 導入
- `@anthropic-ai/claude-code` インストール
- Git初期設定・ワークスペース初期化（README.md / CLAUDE.md / .gitignore）

---

## AI Desktop Agent（STEP10）

- `desktop_observer.py`: ウィンドウ一覧・解像度・スクリーンショットを取得し `desktop-state.json` に保存
- `desktop_controller.py`: `move_mouse` / `click` / `type_text` / `keypress` / `focus_window` のインターフェースを用意
  - 実操作は `status: "not_implemented"` のスタブ（xdotoolが未導入のため）

---

## Desktop Tools（STEP11・開発中）

- `desktop_observer.py` / `desktop_controller.py` を `desktop` パッケージ（`observer.py` / `controller.py` / `planner.py` / `tools.py`）に再構成
- `desktop.controller`: アクションを `desktop-actions.json` にキューイング（`status: "queued"`）
- `desktop.planner`: 指示文からアクションプランを生成する骨組みのみ実装（`DesktopPlanner.plan()` はまだ実際のプランニングロジックなし）
- `desktop.tools.DesktopTools`: Claude Code / 将来のAgentから利用する統一APIとして公開
- ワークスペースに `CLAUDE.md` で利用ルールを明記（実行はまだ未実装であることを明記）

---

# Repository

```
aws-microvm-lab/

common/
  proxy/

docs/

scripts/
  common/
  config/

step1-hello/
step2-terminal/
step3-novnc/
step4-gnome/
step5-firefox/
step6-playwright/
step7-desktop-automation/
step8-code-server/
step9-claude-code/
step10-desktop-agent/
step11-desktop-tools/
```

---

# Current Architecture

```
Browser
        │
        ▼
Local Proxy
        │
 ┌──────┼──────────┬──────────┐
 │      │          │          │
 ▼      ▼          ▼          ▼
ttyd  noVNC   code-server   (future)
 │      │          │
 └──────┴────┬─────┘
             ▼
     AWS Lambda MicroVM
             │
   ┌─────────┼─────────────┬──────────────┐
   │         │             │              │
   ▼         ▼             ▼              ▼
Terminal  Firefox     Playwright     Claude Code
                                          │
                                          ▼
                                   Desktop Tools
                              (observer / controller /
                                planner / tools)
```

---

# Current Development Policy

- STEP単位で実装する
- 各STEPは独立したサンプルとする
- 共通処理は scripts / common に集約
- run.sh から全STEPを起動する
- ドキュメントを同時に更新する

---

# Current Scripts

起動

```bash
./scripts/run.sh step2

./scripts/run.sh step6

./scripts/run.sh step9

./scripts/run.sh step11
```

設定

```
scripts/config/
```

共通起動

```
scripts/common/run-microvm.sh
```

---

# Next Milestone

## STEP11 Desktop Tools（残作業）

- `desktop.controller` の実操作対応（xdotool の代替手段の選定：AL2023標準リポジトリに存在しないため、ソースビルド or 別ツール検討）
- `desktop.planner` に実際のプランニングロジックを実装
- Claude Code から `desktop.tools.DesktopTools` を呼び出すデモの作成

## STEP12 Persistent Workspace

目的

MicroVM停止後も作業内容を保持する。

候補

- GitHub
- S3
- EFS

## STEP13 Multi Agent

複数 MicroVM を利用した並行開発（Frontend / Backend / Testing 等の役割分担）。

---

# Future Ideas

- Claude Desktop
- Gemini CLI
- Codex CLI
- Continue.dev
- MCP Server
- Browser Agent
- Desktop Agent
- AI Pair Programming
- Multi Agent
- Workspace Snapshot
- GitHub Integration

---

# Known Issues

現在の課題

- GUI起動速度
- Desktop起動時間
- Playwrightブラウザサイズ
- xdotool が Amazon Linux 2023 標準リポジトリに存在せず、Desktop操作（クリック・キー入力）が未実装
- Desktop Tools の Planner が骨組みのみで実プランニング未実装
- Snapshot機能
- 永続ストレージ
- EFS/S3連携

詳細は

```
docs/TROUBLESHOOTING.md
```

を参照。

---

# Documents

```
README.md

PROJECT.md

docs/

ROADMAP.md

ARCHITECTURE.md

TROUBLESHOOTING.md
```

---

# Notes

このプロジェクトでは

**「AWS Lambda MicroVM を AI の作業環境として利用する」**

ことをテーマに、

段階的に Desktop・Browser・AI Agent を構築していく。
