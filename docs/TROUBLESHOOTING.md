# Troubleshooting

このドキュメントでは AWS Lambda MicroVM Lab の構築中によく遭遇した問題と、その解決方法をまとめています。

---

# CREATE_FAILED

## 症状

MicroVM Image が

```
CREATE_FAILED
```

になる。

## 確認方法

```bash
aws lambda-microvms get-microvm-image \
  --image-identifier <IMAGE_ARN>
```

## ビルドログ確認

```bash
aws logs tail /aws/lambda-microvms/<IMAGE_NAME> \
  --since 30m
```

---

# Docker Build Error

## 症状

```
failed to solve
```

または

```
Dockerfile:
```

が表示される。

## 確認

ビルドログ

```bash
aws logs tail /aws/lambda-microvms/<IMAGE_NAME> \
  --since 30m
```

---

# No package matches

## 症状

```
No package matches 'xxxx'
```

例

```
No package matches 'ttyd'
```

## 原因

Amazon Linux 2023 Repository に存在しないパッケージ。

## 対応

- GitHub Release を利用
- ソースからビルド
- 代替パッケージを利用

---

# Firefox が真っ黒

## 症状

```
http://localhost:8080/vnc.html
```

へアクセスすると黒い画面のまま。

## 確認

Terminal

```bash
cat /tmp/playwright.log
```

Firefox

```bash
ps -ef | grep firefox
```

Display

```bash
echo $DISPLAY
```

## 原因

多くの場合

- Firefox起動待ち
- Playwright起動中
- Xvfb未起動

---

# Playwright が起動しない

## 症状

```
BrowserType.launch
```

エラー

例

```
BrowserType.launch:
Failed to launch browser
```

## 確認

```bash
cat /tmp/playwright.log
```

## 原因

Playwright用 Firefox が存在しない。

## 対応

Dockerfile

```dockerfile
RUN python3 -m playwright install firefox
```

Python

```python
browser = p.firefox.launch(
    headless=False,
)
```

---

# ttyd が起動しない

## 確認

```bash
ps -ef | grep ttyd
```

## バージョン確認

```bash
ttyd --version
```

## 原因

Amazon Linux Repository に存在しない。

GitHub Release の利用が必要。

---

# noVNC が表示されない

## 確認

```bash
ps -ef | grep websockify

ps -ef | grep x0vncserver
```

ブラウザ

```
http://localhost:8080/vnc.html
```

---

# Xvfb が起動しない

## 確認

```bash
ps -ef | grep Xvfb
```

Display

```bash
echo $DISPLAY
```

期待

```
:1
```

---

# Proxy が 502

## 症状

```
HTTP ERROR 502
```

## 確認

Target Port

```bash
echo $TARGET_PORT
```

Proxy

```bash
ps -ef | grep proxy
```

## 原因

- MicroVM停止
- Port違い
- Token期限切れ

---

# allowed-ports エラー

## 症状

```
Invalid JSON
```

```
Extra data
```

## 原因

Shell の Quote 展開。

## 対応

JSON を手書きしない。

```bash
jq -nc \
  --argjson vnc 6080 \
  --argjson terminal 7681 \
  '[{"port":$vnc},{"port":$terminal}]'
```

---

# Token 作成失敗

## 確認

```bash
aws lambda-microvms create-microvm-auth-token help
```

生成

```bash
aws lambda-microvms create-microvm-auth-token ...
```

---

# Terminal が表示されない

URL

```
http://localhost:8080/terminal/
```

確認

```bash
ps -ef | grep ttyd
```

---

# GUI が表示されない

URL

```
http://localhost:8080/vnc.html
```

確認

```bash
ps -ef | grep x0vncserver

ps -ef | grep Xvfb
```

---

# Proxy Routing

現在

```
/terminal

↓

7681
```

```
/vnc.html

↓

6080
```

---

# 共通起動

現在は

```bash
./scripts/run.sh stepX
```

のみ利用。

例

```bash
./scripts/run.sh step2

./scripts/run.sh step5

./scripts/run.sh step6
```

---

# よく使うデバッグコマンド

## 起動ログ

```bash
cat /tmp/start.log
```

---

## Playwright

```bash
tail -100 /tmp/playwright.log
```

---

## Firefox

```bash
ps -ef | grep firefox
```

---

## X

```bash
ps -ef | grep Xvfb

ps -ef | grep x0vncserver
```

---

## ttyd

```bash
ps -ef | grep ttyd
```

---

## Display

```bash
echo $DISPLAY
```

---

## Port確認

```bash
echo $TARGET_PORT
```

---

## Image状態

```bash
aws lambda-microvms get-microvm-image ...
```

---

## Build Log

```bash
aws logs tail ...
```

---

# Debug Flow

```
ブラウザが表示されない

↓

Proxy確認

↓

Terminal確認

↓

プロセス確認

↓

ログ確認

↓

Dockerfile修正

↓

Image再作成

↓

再起動
```
