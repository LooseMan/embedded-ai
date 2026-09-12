# エージェントと Skill の読み込み仕様・実装手順

この文書は、`agents/` と `skills/` に置いた実験定義を Codex で実行する方法をまとめたものです。

## 1. 用語と現在の状態

このリポジトリには、次の 3 種類のファイルがあります。

| 種類 | このリポジトリでの役割 | `@` で直接呼べるか |
| --- | --- | --- |
| `agents/*.md` | 実験条件と、適用する Skill の一覧を定義するプロファイル | いいえ。Workspace Agent として登録していないため |
| `skills/*/SKILL.md` | Codex に読ませる再利用可能な作業指示 | Skill としてインストール後に `$skill-name` で呼び出す |
| `/コマンド` | Codex 側に実装された組み込みコマンド | ローカル Markdown からは追加できない |

つまり、`agents/legacy-developer.md` を作っただけで `@legacy-developer` が有効になるわけではありません。

## 2. Codex の読み込みの考え方

Codex は起動時に、利用可能なプロジェクト指示と設定済み Skill を初期コンテキストへ取り込みます。プロジェクト指示には `AGENTS.md` などが使われます。指示が複数ある場合は、より具体的な場所の指示が後から適用されます。

Skill は、Skill の検索対象としてインストールまたは設定されているものが自動選択の対象です。リポジトリ内に `skills/` ディレクトリを作っただけでは、必ずしも `$` の候補にはなりません。

Skill とエージェントの指示が競合する場合は、ユーザーの明示的なタスク指示を優先します。実験ではこの競合を避け、両条件に同じタスクを与えてください。

## 3. すぐに実行する方法（現在の構成）

Skill の登録状態に依存しないため、実験の初回はこの方法を推奨します。

### レガシー条件

新しい Codex セッションで、次のように指示します。

```text
agents/legacy-developer.md を実験条件として読み込んでください。
次の Skill を読み込んで、このターンのタスクに適用してください。
- skills/preserve-encoding/SKILL.md
- skills/legacy-euc-jp/SKILL.md

タスク: <ここに共通の評価タスクを書く>
```

### モダン条件

別の新しい Codex セッションで、次のように指示します。

```text
agents/modern-developer.md を実験条件として読み込んでください。
次の Skill を読み込んで、このターンのタスクに適用してください。
- skills/preserve-encoding/SKILL.md
- skills/modern-utf8/SKILL.md

タスク: <ここに共通の評価タスクを書く>
```

各条件で、エージェントに「読み込んだファイル名と適用する文字コードを最初に確認させる」と、測定ログを確認しやすくなります。

## 4. `$skill-name` で呼べるようにする手順

1. 各 Skill を Codex の Skill 検索対象へインストールする。
2. Codex を再起動し、Skill の一覧または候補に `legacy-euc-jp`、`modern-utf8`、`preserve-encoding` が出ることを確認する。
3. 新しいセッションで、次のように明示する。

```text
$legacy-euc-jp $preserve-encoding

タスク: <共通タスク>
```

モダン条件では次を使います。

```text
$modern-utf8 $preserve-encoding

タスク: <共通タスク>
```

Skill の候補に表示されない場合、`$` は使わず、3 のファイルパス指定方式を使います。今回の実行環境では `.codex/` が読み取り専用だったため、リポジトリ内の Skill はまだユーザー環境へインストールされていません。

## 5. `@legacy-developer` で呼べるようにする手順

`@` で選択できるエージェントにするには、Workspace Agent として別途登録します。

1. Workspace Agents の作成画面または対応する管理機能を開く。
2. `agents/legacy-developer.md` の内容を Agent Instructions として登録する。
3. `skills/preserve-encoding/SKILL.md` と `skills/legacy-euc-jp/SKILL.md` を、その Agent の Skill または添付ファイルとして登録する。
4. `legacy-developer` という名前で保存し、必要なら公開する。
5. 新しい会話で `@legacy-developer` を選び、同一タスクを実行する。
6. `modern-developer` も同じ手順で作成する。

この方式では、`@` はエージェントを選択するために使い、文字コードの細かい手順は Agent に登録した Skill に持たせます。

## 6. 測定時の固定条件

- 2 条件で同一のモデル、権限、作業ディレクトリ、入力ファイル、タスク文を使う。
- 各条件を新しいセッションで開始する。
- レガシー条件では `legacy-euc-jp`、`encoding-converter`、`preserve-encoding` を有効にする。
- モダン条件では `modern-utf8`、`encoding-converter`、`preserve-encoding` を有効にする。
- 実行前後の `git diff`、文字コード検証結果、所要時間、ツール呼び出し数、追加修正回数を保存する。
- Skill の読み込み失敗や、別の Skill の自動適用があった場合は、その試行を比較データから除外するか、記録したうえで別試行として扱う。

## 7. 公式仕様との区別

OpenAI の公式資料では、Codex の初期コンテキストに `AGENTS.md` などのプロジェクト指示と、設定済み Skill が組み込まれる仕組みが説明されています。また、Agents API には名前・指示・利用ツールを持つ再利用可能な Agent を作成する API があります。

一方、このリポジトリの `agents/*.md` は実験用のローカル定義であり、Agents API や Workspace Agent の登録処理までは行っていません。

参考:

- [Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Agents API: Create an agent](https://developers.openai.com/api/reference/typescript/resources/beta/subresources/agents/methods/create)
- [Skills API](https://developers.openai.com/api/reference/typescript/resources/skills/methods/list)
