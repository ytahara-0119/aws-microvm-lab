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
- 🔀 共通起動スクリプト
- 🌏 日本語ロケール・タイムゾーン対応
- 🤖 将来的に Claude Code / Desktop Agent を実行予定

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

# Project Structure

```
aws-microvm-lab/

├── common/
│   └── proxy/                 # 共通Proxy
│
├── docs/
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
│
├── scripts/
│   ├── run.sh                 # 共通起動
│   ├── common/
│   │   └── run-microvm.sh
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

# Roadmap

| Step | Description | Status |
|------|-------------|--------|
| STEP1 | Hello MicroVM | ✅ |
| STEP2 | Web Terminal | ✅ |
| STEP3 | noVNC Desktop | ✅ |
| STEP4 | Desktop Environment Survey | ✅ |
| STEP5 | Firefox Desktop | ✅ |
| STEP6 | Playwright Browser Automation | ✅ |
| STEP7 | Desktop Automation | 🚧 |
| STEP8 | code-server | ⏳ |
| STEP9 | Claude Code | ⏳ |
| STEP10 | AI Desktop Agent | ⏳ |
| STEP11 | Persistent Workspace | ⏳ |
| STEP12 | Multi Agent | ⏳ |

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

## STEP5 Firefox

```bash
./scripts/run.sh step5
```

ブラウザ

```
http://localhost:8080/vnc.html
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

# Architecture

```
Browser
          │
          ▼
     Local Proxy
          │
 ┌────────┴────────┐
 │                 │
 ▼                 ▼
ttyd            noVNC
 │                 │
 └────────┬────────┘
          ▼
      AWS Lambda
       MicroVM
          │
 ┌────────┴────────┐
 │                 │
 ▼                 ▼
Terminal       Firefox
                   │
                   ▼
              Playwright
```

詳細は **docs/ARCHITECTURE.md** を参照してください。

---

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
- AI Development Workspace
- AI Desktop Agent

へ段階的に発展させることを目標としています。

---

# Future

今後追加予定

- Desktop Automation
- code-server
- Claude Code
- Claude Desktop
- AI Agent
- GitHub連携
- S3/EFS Workspace
- Multi Agent
- Snapshot / Resume

---

# License

MIT
