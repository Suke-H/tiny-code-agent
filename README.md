# tiny-code-agent

勉強としてかなり最小限のコードエージェントを作ってみた例。

[コードエージェントの話](docs/code-agents.md)

## ファイル構成

```
tiny-code-agent/
├── main.py        # エントリーポイント（REPL ループ）
├── agent.py       # エージェントループ・履歴圧縮
└── tools.py       # ツール定義・実装
```

## セットアップ

```bash
cp .env.example .env   # .env を作成し ANTHROPIC_API_KEY を記入
uv sync
```

## 実行

```bash
uv run --env-file .env python main.py
```

## コマンド

| コマンド | 説明 |
|---------|------|
| `/compact` | 会話履歴を要約して圧縮 |
| `/exit` | 終了 |
