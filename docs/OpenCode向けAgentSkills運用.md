
## 全体構成のメンタルモデル

* **AGENTS.md（プロジェクトの憲法）**：全エージェント・全ツール（Copilot含む）が守るべき共通開発ルール・ビルドコマンド
* **Agents（役割と権限）**：各開発工程（設計・実装・RV・テスト・Ops）を担当する主体。`.opencode/agents/*.md` で定義
* **Skills（オンデマンドな道具）**：特定の作業時のみ読み込む専門手順・ツール。`.opencode/skills/` に集約し、各Agentに装備

---

## 最終推奨ディレクトリ構造

エージェントとスキルをカプセル化（独立化）し、プロジェクト間での再利用性を最大化する**ファイルベース管理パターン**です。

```text
my-project/
├── AGENTS.md                          # 全体共通の基本開発規約（C++20標準、CMake等）
├── .github/
│   └── copilot-instructions.md        # Copilot Edits/Agent ModeにAGENTS.mdを参照させる指示書
├── .opencode/
│   ├── agents/                        # 5工程のエージェント定義（1エージェント1ファイル）
│   │   ├── arch-agent.md
│   │   ├── dev-agent.md
│   │   ├── review-agent.md            # edit: deny（コード破壊防止）
│   │   ├── test-agent.md
│   │   └── ops-agent.md
│   │
│   └── skills/                        # エージェント間で共有・再利用するスキルプール
│       ├── cmake-builder/
│       │   └── SKILL.md
│       ├── asan-analyzer/
│       │   └── SKILL.md
│       ├── static-checker/
│       │   └── SKILL.md
│       └── gtest-gen/
│           └── SKILL.md
└── src/                               # ソースコード

```

---

## 各要素の書き方・設計ルール

### 1. Agents の定義方法 (`.opencode/agents/review-agent.md`)

ファイル先頭の Frontmatter に「モデル」「権限」「装備するスキル」を書き、本文にシステムプロンプトを記述します。

```markdown
---
description: C++のメモリ安全・Modern C++規約・パフォーマンスを検証する専門レビュー担当
mode: subagent
model: openai/gpt-4o
permissions:
  edit: deny             # ★重要: レビュー専門のためコード書き換えは禁止
  bash: allow            # 解析スクリプト等の実行は許可
skills:
  - asan-analyzer        # 必要なスキルだけをID指定で装備（ビルド用スキル等は読み込ませない）
  - static-checker
---

# Review Agent System Prompt
あなたは C++20 に精通したシニア C++ コードレビューエージェントです。
コードの書き換えは行わず、装備された `asan-analyzer` スキル等を活用してメモリリークや非推奨な記述のみを厳格に検証してください。

```

### 2. Skills の定義方法 (`.opencode/skills/asan-analyzer/SKILL.md`)

スキル側には「誰が使うか（Agent名）」は絶対に書かず、「何ができるか（What/When）」のみを記述して疎結合を保ちます。

```markdown
---
name: asan-analyzer
description: AddressSanitizer (ASan) のログを解析し、Use-After-Free や Buffer Overflow の発生箇所と修正案を抽出する。C++のデバッグやメモリ検証時に呼び出す。
---

# Instructions
1. ターミナルで実行された ASan ログ（`asan.log` 等）を読み込みます。
2. エラーアドレスとスタックトレースから該当のソースコード行数を特定します。
3. メモリ解放漏れ・不正アクセスの原因と修正案をフォーマットに従って提示します。

```

---

## 5つのエージェント役割・スキル割り当て一覧

| エージェント | モード | Edit権限 | Bash権限 | 装備スキル (`skills`) |
| --- | --- | --- | --- | --- |
| **`arch-agent`** | Subagent | `/docs/` のみ | 不可 | `doc-generator`, `plantuml-gen` |
| **`dev-agent`** | Primary | 全許可 (`allow`) | 許可 | `cmake-builder`, `git-tools`, `gtest-gen` |
| **`review-agent`** | Subagent | **不可 (`deny`)** | 許可 | `static-checker`, `asan-analyzer` |
| **`test-agent`** | Subagent | `/tests/` のみ | 許可 | `gtest-gen`, `ctest-runner` |
| **`ops-agent`** | Subagent | 設定ファイルのみ | 許可 | `cmake-builder`, `git-tools` |

---

## VSCodeでの使い分け

1. **GitHub Copilot（インライン補完 & Copilot Edits）**
* キーボード入力中のゴーストテキスト（`Tab`で確定）によるリアルタイムコード補完。
* エディタと密結合した小〜中規模なマルチファイル変更。


2. **OpenCode / Codex プラグイン（サブエージェント運用）**
* チャットから `@review-agent` や `@test-agent` を指定して呼び出し。
* **「コードを変更させずに安全に解析だけ行わせる（`edit: deny`）」** ような、工程別の自律的マルチエージェントタスクを実行。
