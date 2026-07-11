# AWS MicroVM Lab

> Build lightweight, browser-accessible development environments on AWS Lambda MicroVM.

AWS Lambda MicroVM を利用して、ブラウザからアクセスできる Linux デスクトップ環境や AI 開発環境を構築する実験プロジェクトです。

最終的には **「数秒で起動できる AI Developer Workspace」** を目指しています。

---

# Features

- 🚀 AWS Lambda MicroVM を利用した軽量実行環境
- 💻 ブラウザから利用できる Linux Desktop
- 🖥 noVNC による GUI
- 🖲 Playwright によるブラウザ自動操作
- 📝 ttyd による Web Terminal
- 🧩 code-server によるブラウザだけの VS Code 環境
- 🤖 Claude Code を MicroVM 上で実行
- 🔍 Desktop 状態観測（ウィンドウ一覧・解像度・スクリーンショット）
- 🔀 共通起動スクリプト
- 🌏 日本語ロケール・タイムゾーン対応
- 🚧 Desktop の実操作（クリック・キー入力）は開発中（xdotool未導入のため未実装）

---

# Demo

## Terminal

```
Browser
    │
    ▼
ttyd
    │
    ▼
Linux Shell
```

---

## Desktop

```
Browser
    │
    ▼
noVNC
    │
    ▼
Xvfb
    │
    ▼
Firefox
```

---

## Playwright

```
Playwright
      │
      ▼
Firefox
      │
      ▼
noVNC
```

Playwright が Firefox を自動操作し、その様子をブラウザからリアルタイムで確認できます。

---

## Cloud IDE + Claude Code

```
Browser
    │
    ▼
code-server (VS Code)
    │
    ▼
Claude Code CLI
```

MicroVM上の code-server と Claude Code CLI を使い、ブラウザだけでAIコーディングができます。

---

## Desktop Tools（開発中）

```
desktop.observer   → Desktop状態・スクリーンショット取得
desktop.controller → アクションのキューイング（実行はまだ未実装）
desktop.planner    → 指示文からアクションプラン生成（骨組みのみ）
desktop.tools      → Claude Code / Agentから使う統一API
```

---

# Project Structure

```
aws-microvm-lab/

├── common/
│   └── proxy/                    # 共通Proxy
│
├── docs/
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
│
├── scripts/
│   ├── run.sh                    # 共通起動
│   ├── common/
│   │   └── run-microvm.sh
│   └── config/
│
├── step1-hello/
├── step2-terminal/
├── step3-novnc/
├── step4-gnome/
├── step5-firefox/
├── step6-playwright/
├── step7-desktop-automation/     # Desktop状態観測
├── step8-code-server/            # ブラウザVS Code
├── step9-claude-code/            # Claude Code CLI
├── step10-desktop-agent/         # Desktop観測 + 操作インターフェース(未実装)
└── step11-desktop-tools/         # desktop パッケージ化（開発中）
```
---

# Roadmap

| Step | Description | Status |
|------|-------------|--------|
| STEP1 | Hello MicroVM | ✅ |
| STEP2 | Web Terminal | ✅ |
| STEP3 | noVNC Desktop | ✅ |
| STEP4 | Desktop Environment Survey | ✅ |
| STEP5 | Firefox Desktop | ✅ |
| STEP6 | Playwright Browser Automation | ✅ |
| STEP7 | Desktop Automation（状態観測） | ✅ |
| STEP8 | code-server | ✅ |
| STEP9 | Claude Code | ✅ |
| STEP10 | AI Desktop Agent（観測のみ） | 🚧 |
| STEP11 | Desktop Tools（パッケージ化） | 🚧 |
| STEP12 | Persistent Workspace | ⏳ |
| STEP13 | Multi Agent | ⏳ |

詳細は **docs/ROADMAP.md** を参照してください。

---

# Quick Start

## STEP2 Terminal

```bash
./scripts/run.sh step2
```

ブラウザ

```
http://localhost:8080/
```

---

## STEP6 Playwright

```bash
./scripts/run.sh step6
```

GUI

```
http://localhost:8080/vnc.html
```

Terminal

```
http://localhost:8080/terminal/
```

---

## STEP9 Claude Code

```bash
./scripts/run.sh step9
```

VS Code（code-server）

```
http://localhost:8080/  (port 8081)
```

Terminal / GUI は STEP6 と同様に利用可能です。

---

## STEP11 Desktop Tools

```bash
./scripts/run.sh step11
```

Desktopの状態取得・アクションキュー確認は MicroVM 内で以下を実行します。

```bash
cd /root/workspace
python3 -m desktop.observer
python3 -m desktop.controller
python3 -m desktop.tools
```

---

# Architecture

```
Browser
          │
          ▼
     Local Proxy
          │
 ┌────────┼────────┬───────────────┐
 │        │        │               │
 ▼        ▼        ▼               ▼
ttyd    noVNC  code-server      (future)
 │        │        │
 └────────┴───┬────┘
              ▼
        AWS Lambda
         MicroVM
              │
 ┌────────────┼──────────────┬──────────────┐
 │            │              │              │
 ▼            ▼              ▼              ▼
Terminal   Firefox      Playwright     Claude Code
                                            │
                                            ▼
                                     Desktop Tools
                                (observer / controller /
                                  planner / tools)
```

詳細は **docs/ARCHITECTURE.md** を参照してください。

---

## Required Environment Variables

Build and image creation require the following environment variables.

```bash
export REGION=ap-northeast-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export BUCKET_NAME="microvm-hello-${ACCOUNT_ID}-${REGION}"
export BUILD_ROLE_ARN=$(aws iam get-role \
  --role-name MicroVMBuildRole \
  --query Role.Arn \
  --output text)
```

# Development


起動方法は全STEP共通です。

```bash
./scripts/run.sh stepX
```

各STEPの設定は

```
scripts/config/
```

で管理しています。

---

# Troubleshooting

よくある問題は

```
docs/TROUBLESHOOTING.md
```

にまとめています。

例

- CREATE_FAILED
- Playwright起動失敗
- Firefoxが真っ黒
- allowed-ports
- Proxy設定

---

# Goals

このプロジェクトでは単なるブラウザ自動操作ではなく、

- Browser Automation
- Desktop Automation
- Cloud IDE / AI Coding
- AI Development Workspace
- AI Desktop Agent

へ段階的に発展させることを目標としています。

---

# Future

今後追加予定

- Desktop 実操作（xdotool代替の選定・実装）
- Desktop Tools の Planner 高度化
- Claude Desktop
- AI Agent連携強化
- GitHub連携
- S3/EFS Workspace（Persistent Workspace）
- Multi Agent
- Snapshot / Resume

---

# License

MIT
