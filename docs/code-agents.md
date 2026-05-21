# コードエージェントの話

### エージェントとは？

- LLM：入力を受け取って出力を返す基盤モデルそのもの
- エージェント：LLMが自らのプロセスとツール使用を動的に指示し、タスクの達成方法を自律的にコントロールするシステム

参考：https://www.anthropic.com/engineering/building-effective-agents

### 自律とは？

特定タスクをやり遂げるために「会話」をすること。単にユーザーとのやり取りだけじゃなく、自身のテキストやツール結果も会話に含める。

「このタスクをして！」という入力からスタートし、

- 「これをするためにツールを使おう」
- （ツールの結果を見て）「うまくいかなかったな。使い方を少し変えてもう一度」
- 「できた。あとはこのツールを使えば」
- 「完了！こうなったよと伝えるか」

### 会話について

ChatGPTなどで会話をすることが増えた世の中。

そもそもLLMはAPIなのでステートレス。会話が成り立つには「前の会話全て」を入力に入れる必要がある

```
[input]
- User: 今日の天気は？

[output]
- AI: 調べるね
- AI: use-tool

[input]
- User: 今日の天気は？
- AI: 調べるね
- AI: use-tool
- Tool: 「雨」

[output]
- AI: 雨だよ

[input]
- User: 今日の天気は？
- AI: 調べるね
- AI: use-tool
- Tool: 「雨」
- AI: 雨だよ
- User: 最近ずっと雨だね

[output]
- AI: そうだねえ。ちょっとまってね
- AI: use-tool

[input]
- User: 今日の天気は？
- AI: 調べるね
- AI: use-tool
- Tool: 「雨」
- AI: 雨だよ
- User: 最近ずっと雨だね
- AI: そうだねえ。ちょっとまってね
- AI: use-tool
- Tool: 「今日は雨、明日は晴れ、明後日も晴れ」

[output]
- AI: 明日から晴れるよ！
```

### コードエージェント

プログラミングタスクに使うエージェント。

ツール: `read_file` / `write_file` / `str_replace` / `run_command` などを用意して会話をすることで、プログラミングをこなす

```
[input]
- User: Pythonで〇×ゲームをgame.pyに作って

[output]
- AI: 作るね
- AI: write_file(path="game.py", content="...")

[input]
- User: Pythonで〇×ゲームをgame.pyに作って
- AI: 作るね
- AI: write_file(path="game.py", content="...")
- Tool: success

[output]
- AI: 書いたよ。動くか確認するね
- AI: run_command(command="python game.py")

[input]
- User: Pythonで〇×ゲームをgame.pyに作って
- AI: 作るね
- AI: write_file(path="game.py", content="...")
- Tool: success
- AI: 書いたよ。動くか確認するね
- AI: run_command(command="python game.py")
- Tool: "SyntaxError: invalid syntax (game.py, line 12)"

[output]
- AI: エラーがあった。直すね
- AI: str_replace(path="game.py", old_str="...", new_str="...")

[input]
- User: Pythonで〇×ゲームをgame.pyに作って
- AI: 作るね
- AI: write_file(path="game.py", content="...")
- Tool: success
- AI: 書いたよ。動くか確認するね
- AI: run_command(command="python game.py")
- Tool: "SyntaxError: invalid syntax (game.py, line 12)"
- AI: エラーがあった。直すね
- AI: str_replace(path="game.py", old_str="...", new_str="...")
- Tool: success

[output]
- AI: run_command(command="python game.py")

[input]
- User: Pythonで〇×ゲームをgame.pyに作って
- AI: 作るね
- AI: write_file(path="game.py", content="...")
- Tool: success
- AI: 書いたよ。動くか確認するね
- AI: run_command(command="python game.py")
- Tool: "SyntaxError: invalid syntax (game.py, line 12)"
- AI: エラーがあった。直すね
- AI: str_replace(path="game.py", old_str="...", new_str="...")
- Tool: success
- AI: run_command(command="python game.py")
- Tool: ""

[output]
- AI: game.py できたよ！エラーもなく動いてる
```

### 会話の要約

見ての通りどんどんinputが膨大になっていくので、トークンを食ってしまう。

そのため/compactが用意されている。仕組みは簡単で、これまでの会話を、それこそLLMに1行に要約してもらう。

```
[input]
- User: Pythonで〇×ゲームをgame.pyに作って
- AI: write_file(path="game.py", content="...")
- Tool: success
- AI: run_command(command="python game.py")
- Tool: "SyntaxError: ..."
- AI: str_replace(path="game.py", old_str="...", new_str="...")
- Tool: success
- AI: run_command(command="python game.py")
- Tool: ""
- AI: game.py できたよ！エラーもなく動いてる
- User: /compact

[output]
- AI: 【要約】game.pyを作成。構文エラーが1件あったが修正済み。現在正常に動作する状態。

[input]
- User: 【要約】game.pyを作成。構文エラーが1件あったが修正済み。現在正常に動作する状態。
- User: それじゃあ次のお願い
```

