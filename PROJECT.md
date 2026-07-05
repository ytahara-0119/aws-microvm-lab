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
- AI Development Workspace

を段階的に構築する。

最終目標は

> **数秒で起動できる AI Developer Workspace**

を実現すること。

---

# Current Status

## Current Step

> **STEP6 Playwright Browser Automation**

現在は STEP6 が完成し、STEP7 Desktop Automation の設計を開始。

---

# Progress

| Step | Status |
|-------|--------|
| STEP1 Hello | ✅ |
| STEP2 Terminal | ✅ |
| STEP3 noVNC | ✅ |
| STEP4 Desktop Survey | ✅ |
| STEP5 Firefox | ✅ |
| STEP6 Playwright | ✅ |
| STEP7 Desktop Automation | 🚧 |
| STEP8 code-server | ⏳ |
| STEP9 Claude Code | ⏳ |
| STEP10 AI Desktop Agent | ⏳ |
| STEP11 Persistent Workspace | ⏳ |
| STEP12 Multi Agent | ⏳ |

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

## Playwright

- Firefox自動起動
- ページ遷移
- スクリーンショット
- GUI確認

---

# Repository

```
aws-microvm-lab/

common/

docs/

scripts/

step1-hello/

step2-terminal/

step3-novnc/

step4-desktop/

step5-firefox/

step6-playwright/
```

---

# Current Architecture

```
Browser
        │
        ▼
Local Proxy
        │
 ┌──────┴──────┐
 │             │
 ▼             ▼
ttyd         noVNC
 │             │
 └──────┬──────┘
        ▼
AWS Lambda MicroVM
        │
 ├──────────────┐
 │              │
 ▼              ▼
Firefox     Playwright
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

./scripts/run.sh step5

./scripts/run.sh step6
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

## STEP7 Desktop Automation

目的

Playwright ではなく

Linux Desktop 全体を操作する。

追加予定

- xdotool
- wmctrl
- xclip
- ImageMagick
- OCR
- Window Control

成果物

```
AIがLinux Desktopを操作する
```

---

## STEP8 code-server

目的

ブラウザだけで VS Code を利用する。

追加

- code-server
- Git
- GitHub CLI
- Node.js
- Python
- Rust

---

## STEP9 Claude Code

目的

MicroVM上で Claude Code を実行する。

---

## STEP10 AI Desktop Agent

Desktop 全体を AI が操作する。

```
Claude

↓

Desktop

↓

VS Code

Terminal

Firefox
```

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
