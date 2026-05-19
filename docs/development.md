# 開発ガイド

## 初回構築

```bash
# 1. 初期化（pyproject.toml, .python-version が作られる）
uv init --no-readme
```

2. `pyproject.toml` に以下を追記する

```toml
[tool.uv]
exclude-newer = "2026-05-12T00:00:00Z"   # 今日 - 7日の日付
```

```bash
# 3. 依存追加（uv.lock が自動生成されインストールまで行われる）
uv add anthropic

# 4. uv.lock にハッシュが入っていることを確認
# hash = "sha256:..." の行が各パッケージにあればOK
cat uv.lock

# 5. .env を作成して ANTHROPIC_API_KEY を記入
cp .env.example .env

# 6. uv.lock をコミット
git add pyproject.toml .python-version uv.lock
git commit -m "init uv environment"
```

## 依存パッケージを追加するとき

```bash
uv add パッケージ名
git add uv.lock
```

## 依存をアップデートするとき

```bash
# pyproject.toml の exclude-newer を「今日 - 7日」の日付に更新してから実行
uv lock --upgrade
git add uv.lock
```

## 実行

```bash
uv run --env-file .env python main.py
```
