# Agent Skills とローカル MCP サーバー

## 役割

- `SKILL.md`: どの依頼で、どの MCP ツールを、どう使うかを定義する。
- MCP サーバー: ツールと処理を提供する。
- `.codex/config.toml`: MCP サーバーの起動方法・接続先を定義する。

Skill に接続コマンドや認証情報を書かず、利用手順と接続設定を分離する。

## stdio 方式（ローカル利用）

Codex が MCP サーバーを子プロセスとして起動し、標準入出力で通信する。サーバー側は
`server.run(transport="stdio")` で起動する。

このリポジトリでは、絶対パスを使わず、リポジトリルートからの相対パスで登録する。

```toml
[mcp_servers.jholiday]
command = "python3"
args = ["mcp/local/scripts/jholiday_mcp.py"]
cwd = "."
startup_timeout_sec = 30
```

`cwd` にホームディレクトリ付きの絶対パスや `~` を書く方法は、リポジトリを別の場所へ
チェックアウトする運用には適さない。特に `config.toml` はシェルを経由して解釈されるとは
限らないため、`cwd = "~/..."` と書いても `~` がホームディレクトリへ展開されず、サーバーが
`Unsupported` になることがある。`cwd = "."` とし、`args` もリポジトリルートからの相対パス
にする。

プロジェクトの `.codex/config.toml` は Git 管理してよい。Codex は信頼済みプロジェクトの
`.codex/config.toml` をプロジェクト設定として読み込むため、チェックアウト先が変わっても
絶対パスなしで同じ設定を使える。ただし、Codex をリポジトリルートで起動し、プロジェクトを
信頼済みにしておく必要がある。設定変更後は Codex を再起動し、`codex mcp get jholiday` と
`codex mcp list` で確認する。

確認すべき設定例:

```toml
[mcp_servers.jholiday]
command = "python3"
args = ["mcp/local/scripts/jholiday_mcp.py"]
cwd = "."
startup_timeout_sec = 30
```

`Unsupported` の場合は、次の順に確認する。

1. `codex mcp get jholiday` で `cwd` が `.` になっているか確認する。
2. `python3` が PATH にあり、依存パッケージを同じ Python 環境へインストールしているか確認する。
3. リポジトリルートで `python3 mcp/local/scripts/jholiday_mcp.py` を実行し、起動時エラーがないか確認する。
4. MCP サーバーの標準出力へログを出していないか確認する。stdio の標準出力は MCP 通信用なので、ログは標準エラー出力へ出す。

前提は、リポジトリルートで Codex を起動し、`python3` が PATH にあること。初回のみ依存
パッケージをインストールする。

```bash
python3 -m pip install -r mcp/local/scripts/requirements.txt
codex mcp list
codex mcp get jholiday
```

CLI で登録する場合:

```bash
codex mcp add jholiday -- python3 mcp/local/scripts/jholiday_mcp.py
```

## Skill からの利用

Skill には次の5点を明記する。

1. MCP サーバー名（この例では `jholiday`）
2. ツール名（この例では `check_holiday`）
3. 入力形式（`target_date` に `YYYY-MM-DD`）
4. 結果の解釈（`is_holiday`、`holiday_name`、`date`）
5. ツールが使えない場合のフォールバック

例:

```markdown
## MCP ツール

祝日の判定には `jholiday` の `check_holiday` を使う。

- `target_date` は `YYYY-MM-DD` 形式で渡す。
- `holiday_name` を回答に使用する。
- 空の場合は国民の祝日ではないと扱う。
- 会社休日・年末年始休業とは区別する。
- MCP が使えない場合は、その事実と代替手段・情報源を明示する。
```

Skill 名と MCP 登録名は自動連携しないため、Skill に書くサーバー名と
`[mcp_servers.<名前>]` の名前を一致させる。

## 動作確認

1. 依存パッケージをインストールする。
2. `codex mcp get jholiday` で設定を確認する。
3. 新しい Codex セッションを開始する。
4. Skill が適用される依頼を実行する。

ツールが表示されない場合は、作業ディレクトリ、`python3` の PATH、依存パッケージ、
相対パス、Codex の再起動を確認する。stdio の標準出力には通信を妨げるログを出さず、
ログは標準エラー出力へ出す。

## HTTP 方式

HTTP は起動済みの共有サーバーへ接続する方式で、複数利用者・別ホスト向けである。
エンドポイント、HTTPS、認証・認可、入力検証、タイムアウト、エラー応答を設定する。
ローカル開発や個人利用には stdio が適している。

## 安全上の注意

- API キーやトークンを `SKILL.md` や設定ファイルへ直書きしない。
- 認証なしで MCP サーバーをインターネットへ公開しない。
- 外部 MCP は提供者と実装を確認してから登録する。
- 書き込み系ツールには対象・権限・確認手順を設ける。

要点は、Skill が「いつ何を使うか」、MCP 設定が「どう接続するか」、MCP サーバーが
「何を実行するか」を担当するよう分けることである。
