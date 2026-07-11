# Architecture

> AWS Lambda MicroVM Lab Architecture

このドキュメントでは AWS Lambda MicroVM Lab のシステム構成について説明します。

---

# Design Philosophy

このプロジェクトでは、

**「軽量な Linux Desktop を数秒で起動し、ブラウザから利用できる AI Workspace を構築する」**

ことを目的としています。

設計方針

- 各STEPは独立したサンプル
- 共通処理は common / scripts に集約
- 起動方法を統一
- Browser First
- Stateless を基本とする

---

# High Level Architecture

```
                        Browser

                           │

              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼

          Terminal                  Desktop

          (/terminal)             (/vnc.html)

              │                         │

              └────────────┬────────────┘
                           │

                    Local Proxy

                           │

                           ▼

               AWS Lambda MicroVM

                           │

       ┌──────────┬──────────┬──────────┐
       │          │          │
       ▼          ▼          ▼

    Terminal   Firefox   Playwright

```

---

# Repository Architecture

```
aws-microvm-lab/

├── common/
│   └── proxy/
│
├── docs/
│
├── scripts/
│   ├── common/
│   └── config/
│
├── step1-hello/
├── step2-terminal/
├── step3-novnc/
├── step4-gnome/
├── step5-firefox/
├── step6-playwright/
├── step7-desktop-automation/
├── step8-code-server/
├── step9-claude-code/
├── step10-desktop-agent/
└── step11-desktop-tools/
```

---

# Runtime Architecture

```
Mac

│

├── Browser

├── AWS CLI

├── Local Proxy

└── run.sh
         │
         ▼

Lambda MicroVM

         │

 ┌───────┴────────┐

 │                │

 ▼                ▼

GUI           Terminal

 │                │

 ▼                ▼

Firefox       ttyd
```

---

# Common Scripts

現在はすべてのSTEPで共通の起動方法を採用している。

```
./scripts/run.sh stepX
```

例

```
./scripts/run.sh step2

./scripts/run.sh step5

./scripts/run.sh step6
```

処理

```
run.sh

↓

stepX.env

↓

run-microvm.sh

↓

run-microvm

↓

Auth Token

↓

Proxy

↓

Browser
```

---

# Network Architecture

```
Browser

↓

http://localhost:8080

↓

Local Proxy

↓

AWS Lambda MicroVM Endpoint
```

現在のRouting

| URL | Port |
|------|------|
| / | TARGET_PORT |
| /terminal | 7681 |
| /vnc.html | 6080 |
| code-server（STEP8以降） | 8081 |

---

# Desktop Architecture

```
Browser

↓

noVNC

↓

websockify

↓

TigerVNC

↓

Xvfb

↓

Desktop
```

GUI Application

```
Firefox

Playwright

VS Code (code-server)

今後追加予定

Calculator

Image Viewer
```

---

# Terminal Architecture

```
Browser

↓

ttyd

↓

bash

↓

Linux
```

Terminal は GUI が起動しない場合のデバッグ環境として利用する。

---

# Browser Automation

STEP6

```
Playwright

↓

Firefox

↓

Web Browser
```

Playwright は Desktop 上の Firefox を操作する。

操作例

- ページ遷移
- 入力
- Click
- Screenshot

---

# Desktop Automation (Completed)

STEP7

xdotool / wmctrl / xclip は Amazon Linux 2023 標準リポジトリに存在しないため、実装は Desktop の状態観測に着地した。

```
AI

↓

Desktop Observation

↓

xwininfo / xrandr / xlsclients

ImageMagick (screenshot)

↓

desktop-state.json
```

マウス操作・OCRなどの実操作は STEP10 / STEP11 で継続対応中。

---

# Cloud IDE (Completed)

STEP8

```
Browser

↓

code-server

↓

VS Code
```

ブラウザのみで開発環境を提供する。

---

# AI Coding (Completed)

STEP9

```
Claude Code CLI

↓

VS Code (code-server)

↓

Git

↓

Build

↓

Test
```

npm経由で `@anthropic-ai/claude-code` を導入し、MicroVM上でAIコーディングを行う。

---

# AI Desktop Agent (In Progress)

STEP10

```
desktop_observer.py

↓

xwininfo / xrandr / xlsclients / import

↓

desktop-state.json / desktop.png

desktop_controller.py

↓

move_mouse / click / type_text / keypress / focus_window

↓

status: not_implemented (xdotool未導入)
```

観測（Observer）は実装済み。実操作（Controller）はインターフェースのみで、xdotoolの代替手段が未選定のため未実装。

---

# Desktop Tools (In Progress)

STEP11

STEP10の `desktop_observer.py` / `desktop_controller.py` を再利用可能なPythonパッケージに再構成。

```
desktop/
  ├── observer.py    Desktop状態・スクリーンショット取得
  ├── controller.py  アクションをキューに追加（実行はまだ未実装）
  ├── planner.py     指示文からアクションプラン生成（骨組みのみ）
  └── tools.py        DesktopTools（Claude Code / Agent向け統一API）
```

```
Claude Code

↓

desktop.tools.DesktopTools

↓

observe() / plan() / move_mouse() / click() / type_text() / keypress()
```

`desktop.controller` はアクションを `desktop-actions.json` にキューイングするところまで実装済み。実際のマウス・キーボード操作の実行は未実装。

---

# Persistent Workspace (Planned)

STEP12

```
GitHub

S3

EFS

↓

Workspace

↓

MicroVM
```

Workspace を再利用可能にする。

---

# Multi Agent (Planned)

STEP13

```
Agent A

↓

Frontend

──────────────

Agent B

↓

Backend

──────────────

Agent C

↓

Testing
```

複数 MicroVM を利用した開発。

---

# Configuration

各STEPの設定は

```
scripts/config/
```

で管理する。

例

```
step2.env

step6.env

step9.env

step11.env
```

---

# Common Components

共通利用

```
scripts/run.sh

scripts/common/run-microvm.sh

common/proxy
```

STEP固有

```
Dockerfile

start.sh

Application
```

---

# Design Principles

共通処理は必ず scripts に集約する。

STEPごとの差分だけを各ディレクトリに持つ。

```
Common

↓

run.sh

Proxy

MicroVM Launcher

↓

STEP

↓

Dockerfile

Application
```

---

# Future Architecture

最終形

```
Browser

↓

Proxy

↓

AWS Lambda MicroVM

↓

Linux Desktop

↓

VS Code

↓

Claude Code

↓

Desktop Agent

↓

Workspace

↓

Multi Agent
```

---

# Current Status

完成

- Hello
- Terminal
- noVNC
- Desktop
- Firefox
- Playwright
- Desktop Automation（状態観測のみ）
- code-server
- Claude Code

開発中

- AI Desktop Agent（観測は完了、実操作は未実装）
- Desktop Tools（observer/controller/planner/toolsパッケージ化）

予定

- Desktop 実操作の実装（xdotool代替の選定）
- Persistent Workspace
- Multi Agent