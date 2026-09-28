Playwrightの `codegen` を使った、最も効率的なブラウザ自動化・バッチスクリプトの作成・運用手順です。

---

### Step 1: 環境準備

Python環境に Playwright とブラウザ本体をインストールします。

```bash
pip install playwright
playwright install

```

---

### Step 2: `codegen` で操作を録画してスクリプト生成

対象のWebサイトを指定して `codegen` を実行します（`-o` オプションで出力ファイル名を指定）。

```bash
playwright codegen https://example.com -o script.py

```

1. 自動でブラウザとコード生成ウィンドウが立ち上がります。
2. 画面上で通常通りログインやボタンクリック、フォーム入力を行います。
3. 操作に対応した Python（Sync版）のコードがリアルタイムで `script.py` に書き出されます。
4. 操作が終わったらブラウザを閉じるだけで完了です。

---

### Step 3: 生成された Python スクリプトの微調整

`codegen` で生成された `script.py` は、そのまま実行可能な状態になっています。

```python
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    # headless=True に変更すればバックグラウンド実行になります
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # codegenで録画された操作手順
    page.goto("https://example.com/login")
    page.get_by_placeholder("ユーザー名").fill("my_user")
    page.get_by_placeholder("パスワード").fill("my_password")
    page.get_by_role("button", name="ログイン").click()

    # 必要に応じてデータ抽出やスクショ保存処理を追記
    # page.screenshot(path="result.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

```

**調整のコツ:**

* **Headless化**: 本番運用時は `launch(headless=True)` にしてバックグラウンド実行させます。
* **環境変数の切り出し**: パスワードやURLなどの動的データは `os.environ` に置き換えます。
* **固定IDへの変更**: 日付や検索結果など「毎回文言が変わる要素」を操作した箇所は、安定した属性（`id` や `data-testid` 等）に書き換えておくとより壊れにくくなります。

---

### Step 4: 定期実行とエラー時の対応（Self-Healing）

* **通常運用（費用$0・高速）**:
作成した `script.py` を cron、GitHub Actions、あるいはローカルのバッチ処理として直接実行します。
* **サイト修復（エラー発生時のみLLMを使用）**:
UI変更などでスクリプトが停止した場合のみ、エラーログとHTML/スクリーンショットをLLMに渡し、`script.py` のセレクター部分だけを自動修復させます。
