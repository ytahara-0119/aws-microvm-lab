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

> **STEP15 Browser Search Agent**

STEP12 Desktop Executor で、`xdotool` が使えない問題を `python-xlib` + XTest 拡張への切り替えで解決し、マウス移動・クリック・キー入力・文字入力などの実操作が実際に動くようになった。

STEP13 Desktop Agent Loop では、Observe → Claude Codeによるプラン生成 → ポリシー検証 → 人間の承認 → 実行 → 再Observe という一連のループを実装し、プロジェクトの最終目標である「AIがLinux Desktopを操作する」がひとまず動く形で実現した。

STEP14 Desktop Orchestrator では、`desktop.agent` CLIをラップする `python3 -m desktop.orchestrator request/approve/execute/status` を追加し、一連の操作をより簡潔に呼び出せるようにした。

STEP15 Browser Search Agent では、複合アクション `browser_search`（アドレスバーへURLを直接入力してWeb検索）と `vision_read`（画面を撮影しClaudeに読ませてJSONで結果を返す）を新規実装。

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

上記の一連の流れを、実際に

```bash
python3 -m desktop.orchestrator request \
  'Search the web for "AWS Lambda MicroVM", wait until the page loads, read the title of the first search result, and return it as JSON.'
```

というコマンド1つから最後まで動作確認済み（DuckDuckGoで検索し、`first_result_title: "AWS Lambda MicroVMs"` を正しく返すところまで確認）。

実装中に見つかった `desktop/executor.py` の `SHIFTED_CHARACTERS` テーブルのバグ（`"="` を誤って `Shift+"-"`＝`"_"` に対応付けていたため、URLの `=` が `_` に化けていた）を修正し、STEP12〜15すべてのexecutor.pyに反映済み。

完全自律ループ（承認なしの自動実行）や複数MicroVMでの並行実行は未着手。

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
| STEP10 | AI Desktop Agent（観測 + 操作インターフェース定義） | ✅ |
| STEP11 | Desktop Tools（observer/controller/planner/tools 化） | ✅ |
| STEP12 | Desktop Executor（python-xlibによる実操作） | ✅ |
| STEP13 | Desktop Agent Loop（Observe→Plan→Approve→Execute） | ✅ |
| STEP14 | Desktop Orchestrator（request/approve/execute/status CLI） | ✅ |
| STEP15 | Browser Search Agent（browser_search + vision_read） | ✅ |
| STEP16 | Persistent Workspace | ⏳ |
| STEP17 | Multi Agent | ⏳ |

※ 当初ロードマップの STEP11「Persistent Workspace」は、実際の開発では「Desktop Tools」「Desktop Executor」「Desktop Agent Loop」「Desktop Orchestrator」「Browser Search Agent」の実装が優先され、Persistent Workspace / Multi Agent は STEP16 / STEP17 に繰り下げ。

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
  - この時点では実操作は `status: "not_implemented"` のスタブ（xdotoolが未導入のため）。実装はSTEP12で解決。

---

## Desktop Tools（STEP11）

- `desktop_observer.py` / `desktop_controller.py` を `desktop` パッケージ（`observer.py` / `controller.py` / `planner.py` / `tools.py`）に再構成
- `desktop.controller`: アクションを `desktop-actions.json` にキューイング（`status: "queued"`）
- `desktop.tools.DesktopTools`: Claude Code / 将来のAgentから利用する統一APIとして公開
- ワークスペースに `CLAUDE.md` で利用ルールを明記

---

## Desktop Executor（STEP12）

xdotoolがAL2023に存在しない問題を、`python-xlib` + X11 XTest拡張への切り替えで解決。

- `desktop.executor.DesktopExecutor`: X11のXTest拡張を使い、実際にマウス移動・クリック・ダブルクリック・スクロール・キー入力・文字入力・キーの組み合わせを実行
- `desktop-actions.json` のアクションキューを読み込んで順次実行し、結果を `desktop-execution.json` に保存
- 日本語含む文字入力は現状ASCII中心（Shiftキー処理込みの`type_text`実装）

---

## Desktop Agent Loop（STEP13）

プロジェクトの最終目標「AIがLinux Desktopを操作する」を、人間承認を挟んだ閉ループとして実現。

- `desktop.agent.DesktopAgent`: `observe → create_plan_with_claude → approve → execute → observe` の一連の流れを提供
- `desktop.claude_planner.ClaudePlanner`: `claude -p` でClaude Code CLIを呼び出し、`prompts/agent-prompt.md`のシステムプロンプト + 現在のDesktop状態からアクションプラン（JSON）を生成
- `desktop.policy`: 許可アクションのホワイトリスト化、危険な文字列（`rm -rf /`, `shutdown`等）やキー操作（Alt+F4, Ctrl+Alt+Delete）のブロックといった安全策
- CLI (`python3 -m desktop.agent`): `observe` / `plan` / `show-plan` / `approve` / `execute` / `status` / `show-result` / `clear` の各コマンドを提供し、必ず人間の承認（approve）を経てから実行される

---

## Desktop Orchestrator（STEP14）

`desktop.agent` CLIをサブプロセス経由でラップし、より簡潔な操作フローを提供。

- `desktop.orchestrator.DesktopOrchestrator`: `request`（observe→planを一括実行）/ `approve` / `execute` / `status` を提供
- CLI (`python3 -m desktop.orchestrator`): 1つの自然言語指示から `observe → plan` までを1コマンドで実行できる

---

## Browser Search Agent（STEP15）

「AIがブラウザで検索し、結果をVisionで読んで返す」という具体的なデモを通して、Desktop Agent Loopの実用性を検証。

- `desktop.executor.DesktopExecutor.browser_search(query, engine)`: アドレスバーにフォーカス（Ctrl+L）→検索URLを入力→Enter、という座標に依存しない検索実行。既定の検索エンジンはDuckDuckGo
- `desktop.vision.VisionReader`: `claude_planner.py`と同じsubprocess方式で `claude -p` を呼び出し、直近のスクリーンショットをClaudeに読ませて `status` / `first_result_title` / `confidence` / `reason` のJSONを返させる
- `vision_read` アクション: 実行時に画面を撮り直してからClaude Visionに渡すため、プラン中のどの位置に置いても最新の画面を読める
- `desktop.policy`: `browser_search` / `vision_read` を許可アクションに追加し、空文字・長すぎる入力・危険な文字列を拒否
- `prompts/agent-prompt.md` / `prompts/vision-prompt.md`: 新アクションの仕様とルールを追記
- 実機確認済み: `python3 -m desktop.orchestrator request '...'` → `approve` → `execute` の一連の流れで、DuckDuckGo検索結果の1件目タイトルを正しくJSONで取得
- 実装中に発覚した `desktop/executor.py` の `SHIFTED_CHARACTERS` バグ（`"="` の入力が `"_"` になる）を修正し、STEP12〜15全てに反映

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
step12-desktop-executor/
step13-desktop-agent-loop/
step14-desktop-orchestrator/
step15-browser-search-agent/
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

./scripts/run.sh step12

./scripts/run.sh step14

./scripts/run.sh step15
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

## STEP15 Browser Search Agent（残作業）

- `vision_read` のJSONスキーマを `first_result_title` 固定ではなく汎用化（現状はこのデモ用途に特化）
- Google等、DuckDuckGo以外の検索エンジンでの動作確認
- 承認なしの自律実行モード（安全性の検証がある程度進んでから）
- 日本語入力など`type_text`の対応文字種拡大
- ポリシー（`desktop.policy`）のルール拡充

## STEP16 Persistent Workspace

目的

MicroVM停止後も作業内容を保持する。

候補

- GitHub
- S3
- EFS

## STEP17 Multi Agent

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
- `desktop.policy` の安全ルールが単純なキーワードブロックのみで、包括的ではない
- `type_text` の日本語等マルチバイト文字入力は未対応（ASCII中心）
- `vision_read` のJSONスキーマが `first_result_title` 固定で汎用化されていない
- `browser_search` は現状DuckDuckGo想定。Google等は同意ダイアログ等で失敗する可能性が高く未検証
- 現状は人間の承認（approve）を挟む半自動フローのみ。完全自律実行は未着手
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
