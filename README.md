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
- 🖱 python-xlib(XTest) による実際のマウス・キーボード操作
- 🧠 Claude Code が Desktop状態から操作プランを生成し、人間承認を経て実行するAgentループ
- 🔎 `browser_search` + `vision_read` で「検索して結果を読む」をAIが完結できる
- 🔀 共通起動スクリプト
- 🌏 日本語ロケール・タイムゾーン対応

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

## Desktop Tools

```
desktop.observer   → Desktop状態・スクリーンショット取得
desktop.controller → アクションのキューイング
desktop.executor   → python-xlib(XTest)で実際にマウス・キーボードを操作
desktop.tools      → Claude Code / Agentから使う統一API
```

---

## Desktop Agent Loop

```
observe
  │
  ▼
Claude Code がプラン生成 (claude -p)
  │
  ▼
policy検証（許可アクションのみ・危険操作をブロック）
  │
  ▼
人間が承認 (approve)
  │
  ▼
実行 (execute) → 再度observe → 結果保存
```

`python3 -m desktop.agent plan "<指示>"` → `approve` → `execute` という流れで、AIが提案したDesktop操作を人間が確認してから実行できます。

---

## Browser Search Agent

```
自然言語の指示
    ↓
Claude Planner
    ↓
Human Approval
    ↓
browser_search（アドレスバーに直接URLを入力して検索）
    ↓
検索結果をスクリーンショット
    ↓
vision_read（Claude Visionが画像を読む）
    ↓
最初の検索結果タイトルをJSONで返す
```

`python3 -m desktop.orchestrator request '...'` の1コマンドから、実際にDuckDuckGoで検索して1件目の検索結果タイトルをJSONで取得するところまで動作確認済みです。

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
├── step10-desktop-agent/         # Desktop観測 + 操作インターフェース定義
├── step11-desktop-tools/         # desktop パッケージ化
├── step12-desktop-executor/      # python-xlibによる実操作
├── step13-desktop-agent-loop/    # Observe→Plan→Approve→Execute ループ
├── step14-desktop-orchestrator/  # request/approve/execute/status CLI
└── step15-browser-search-agent/  # browser_search + vision_read
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
| STEP10 | AI Desktop Agent（観測 + 操作インターフェース定義） | ✅ |
| STEP11 | Desktop Tools（パッケージ化） | ✅ |
| STEP12 | Desktop Executor（python-xlibで実操作） | ✅ |
| STEP13 | Desktop Agent Loop（Observe→Plan→Approve→Execute） | ✅ |
| STEP14 | Desktop Orchestrator（request/approve/execute/status CLI） | ✅ |
| STEP15 | Browser Search Agent（browser_search + vision_read） | ✅ |
| STEP16 | Persistent Workspace | ⏳ |
| STEP17 | Multi Agent | ⏳ |

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

## STEP15 Browser Search Agent

```bash
./scripts/run.sh step15
```

MicroVM 内で以下を実行すると、自然言語の指示1つからWeb検索→結果読み取りまでをAIが行います。

```bash
cd /root/workspace

# 指示を渡してobserve→planを実行
python3 -m desktop.orchestrator request \
  'Search the web for "AWS Lambda MicroVM", wait until the page loads, read the title of the first search result, and return it as JSON.'

# 内容を確認して承認
python3 -m desktop.agent show-plan
python3 -m desktop.orchestrator approve

# 実行
python3 -m desktop.orchestrator execute

# 結果確認（vision_readのJSON結果を含む）
python3 -m desktop.agent show-result
```

より基本的なDesktop Agent Loopの単体確認（observe/plan/approve/execute）をしたい場合は STEP13/STEP14 でも同様に動作します。

```bash
./scripts/run.sh step13
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
                                   Desktop Orchestrator
                              (request/approve/execute/status)
                                            │
                                            ▼
                                    Desktop Agent Loop
                               observe → plan(Claude) →
                               policy → approve → execute
                                            │
                                            ▼
                                     Desktop Executor
                          (python-xlib + XTest: move/click/type/
                           keypress/browser_search/vision_read)
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

- `vision_read` のJSONスキーマ汎用化
- Google等、DuckDuckGo以外の検索エンジン対応
- 承認なしの自律実行モード
- 日本語等マルチバイト文字入力への対応
- ポリシー（安全ルール）の拡充
- Claude Desktop
- GitHub連携
- S3/EFS Workspace（Persistent Workspace）
- Multi Agent
- Snapshot / Resume

---

# License

MIT
