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
├── step4-desktop/
├── step5-firefox/
└── step6-playwright/
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

今後追加予定

VS Code

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

# Desktop Automation (Planned)

STEP7

```
AI

↓

Desktop Automation

↓

xdotool

wmctrl

xclip

ImageMagick

OCR

↓

Desktop
```

ブラウザだけではなく Desktop 全体を操作する。

---

# Cloud IDE (Planned)

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

# AI Coding (Planned)

STEP9

```
Claude Code

↓

VS Code

↓

Git

↓

Build

↓

Test
```

AI が開発を支援する。

---

# AI Desktop Agent (Planned)

STEP10

```
AI

↓

Vision

↓

Desktop

↓

VS Code

↓

Terminal

↓

Firefox
```

AI が Linux Desktop を直接操作する。

---

# Persistent Workspace (Planned)

STEP11

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

STEP12

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

step5.env

step6.env
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

開発中

- Desktop Automation

予定

- code-server
- Claude Code
- Desktop Agent
- Persistent Workspace
- Multi Agent