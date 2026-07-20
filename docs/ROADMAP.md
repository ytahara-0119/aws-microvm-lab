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

✅ Completed（状態観測のみ。実操作はSTEP12で実装）

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
- `desktop_controller.py`: move_mouse / click / type_text / keypress / focus_window のインターフェースのみ実装。この時点の実操作は `status: "not_implemented"`（xdotool未導入のため）。実行部分はSTEP12で実装。

Status

✅ Completed（観測とインターフェース定義。実操作の実装はSTEP12に引き継ぎ）

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
- `desktop.controller`: アクションを `desktop-actions.json` にキューイング（`status: "queued"`。実行はSTEP12で対応）
- `desktop.planner`: 指示文からアクションプランを生成する骨組み（ルールベースの簡易版。STEP13でClaude Code版に置き換え）
- `desktop.tools.DesktopTools`: 上記をまとめた統一API

Status

✅ Completed

---

# Phase 8

## Desktop Executor

---

## STEP12 Desktop Executor

### Goal

STEP10/11で「未実装」だったマウス・キーボードの実操作を、実際に動く形で実装する。

### Learn

- xdotoolがAmazon Linux 2023の標準リポジトリに存在しない問題への対処
- `python-xlib` と X11 XTest拡張によるネイティブな入力イベント生成

### Deliverables

- `desktop.executor.DesktopExecutor`: move_mouse / click / double_click / scroll / keypress / key_combination / type_text を X11 XTest拡張で実行
- `desktop-actions.json` のアクションキューを読み込んで順次実行し、結果を `desktop-execution.json` に保存
- Shift操作込みの文字入力（ASCII中心）

Status

✅ Completed

---

# Phase 9

## Desktop Agent Loop

---

## STEP13 Desktop Agent Loop

### Goal

Observe → Plan（Claude Code） → 承認 → Execute → 再Observe という閉ループを実装し、「AIがLinux Desktopを操作する」を実際に動く形で実現する。

### Learn

- Claude Code CLI (`claude -p`) をサブプロセスから呼び出すプランナー設計
- プロンプト設計（`prompts/agent-prompt.md`）でJSON形式のアクションプランを生成させる
- 実行前の安全策（ポリシー検証）の設計

### Deliverables

- `desktop.agent.DesktopAgent`: `observe` / `create_plan_with_claude` / `approve` / `execute` / `run_approved_plan` を提供
- `desktop.claude_planner.ClaudePlanner`: Desktop状態とユーザー指示からClaude CodeにJSON形式のアクションプランを生成させる
- `desktop.policy`: 許可アクションのホワイトリスト、危険な文字列（`rm -rf /`等）やキー操作（Alt+F4, Ctrl+Alt+Delete）のブロック
- CLI (`python3 -m desktop.agent`): observe / plan / show-plan / approve / execute / status / show-result / clear

### 現状

- 実行には必ず人間の承認（`approve`）が必要な半自動フロー
- 完全自律実行（承認なし）は未実装
- 日本語等マルチバイト文字の`type_text`は未対応

Status

✅ Completed

---

# Phase 10

## Desktop Orchestrator

---

## STEP14 Desktop Orchestrator

### Goal

STEP13の`desktop.agent` CLIをラップし、より簡潔な操作フローを提供する。

### Learn

- サブプロセス経由でCLIコマンドを組み合わせるオーケストレーション設計

### Deliverables

- `desktop.orchestrator.DesktopOrchestrator`: `request`（observe→planを一括実行）/ `approve` / `execute` / `status`
- CLI (`python3 -m desktop.orchestrator`)

Status

✅ Completed

---

# Phase 11

## Browser Search Agent

---

## STEP15 Browser Search Agent

### Goal

「自然言語の指示でWeb検索を行い、結果をVisionで読んで返す」という具体的なユースケースを通して、Desktop Agent Loopの実用性を検証する。

```
自然言語の指示
    ↓
Claude Planner
    ↓
Human Approval
    ↓
browser_search（Firefoxをキーボード・マウスで操作）
    ↓
検索結果をスクリーンショット
    ↓
vision_read（Claude Visionが画像を読む）
    ↓
最初の検索結果タイトルをJSONで返す
```

### Learn

- 座標に依存しないブラウザ操作（アドレスバー経由のURL直接入力）
- Claude Codeの画像読み取り（Vision）をsubprocess経由で呼び出す設計
- 複合アクション（`browser_search`）と非入力系アクション（`vision_read`）をどちらも同じExecutorの実行ループに載せる設計

### Deliverables

- `desktop.executor.DesktopExecutor.browser_search(query, engine)`: Ctrl+Lでアドレスバーへフォーカス→検索URL入力→Enter（既定エンジンはDuckDuckGo）
- `desktop.vision.VisionReader`: `claude -p` でスクリーンショットを読み取らせ、`status` / `first_result_title` / `confidence` / `reason` のJSONを返す
- `vision_read`アクション: 実行時に画面を撮り直してから読むため、プラン中どこに置いても最新の画面を読める
- `desktop.policy`に`browser_search` / `vision_read`を追加（空文字・長すぎる入力・危険な文字列を拒否）
- `prompts/agent-prompt.md` / `prompts/vision-prompt.md`の追記

### 実機確認

```bash
python3 -m desktop.orchestrator request \
  'Search the web for "AWS Lambda MicroVM", wait until the page loads, read the title of the first search result, and return it as JSON.'
```

DuckDuckGoで検索し、`first_result_title: "AWS Lambda MicroVMs"`を正しく返すところまで確認済み。

### 副産物: SHIFTED_CHARACTERS バグ修正

実装・検証の過程で`desktop/executor.py`の`SHIFTED_CHARACTERS`テーブルに誤りを発見（`"="`を誤って`Shift+"-"`＝`"_"`に対応付けていたため、URLに含まれる`=`が`_`に化けていた）。STEP12〜15すべてのexecutor.pyに修正を反映。

Status

✅ Completed

---

# Phase 12

## Persistent Workspace

---

## STEP16 Persistent Workspace

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

# Phase 13

## Multi Agent

---

## STEP17 Multi Agent

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



