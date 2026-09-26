# pdf2md.py

PDF を Markdown に変換するためのツールです。PDF の文字・座標・表・図形を
`pdfplumber` で解析し、見出し、番号付きリスト、箇条書き、表をできるだけ維持します。

このツールは LLM、Gemini、OpenAI、`markitdown` パッケージを使用しません。変換結果は
入力 PDF の構造と抽出精度に基づく決定的な出力です。

## 必要環境

- Python 3.10 以上（動作確認: Python 3.12）
- `pdfplumber`

## 導入

`tools` ディレクトリで実行します。

```bash
cd tools
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell の場合:

```powershell
cd tools
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 使い方

入力 PDF を第一引数に指定し、標準出力を Markdown ファイルへリダイレクトします。

```bash
python pdf2md.py input.pdf > output.md
```

例:

```bash
python pdf2md.py 要件定義書_sample.pdf > 要件定義書_sample.md
```

ヘルプを表示する場合:

```bash
python pdf2md.py --help
```

入力ファイルが存在しない場合、または `.pdf` 以外を指定した場合はエラーになります。

## 変換内容

- 大きい見出しを `##`、中見出しを `###` として出力
- PDF 内のベクター図形として描かれた箇条書きを `-` に変換
- PDF 内の `・`、`●` 文字を `-` に変換
- `1.`、`2.` などの番号付きリストは順序を維持
- PDF の表を Markdown のパイプ形式へ変換
- PDF の互換文字を比較時だけ正規化

トップレベルの `#` は文書タイトル用に予約しています。現在の変換では、本文の見出しを
`##` または `###` として出力します。

## パラメータ調整

`pdf2md.py` 冒頭の定数を調整します。変更後は同じ PDF を再変換して結果を確認します。

```python
HEADING_FONT_SIZES = {18, 21}
TOP_LEVEL_HEADING_SIZE = 21
PDF_BULLET_MAX_X = 50
PDF_BULLET_MAX_SIZE = 6
PDF_BULLET_Y_TOLERANCE = 3
```

### 見出し

`HEADING_FONT_SIZES` は見出し候補として認識する PDF のフォントサイズです。

```python
HEADING_FONT_SIZES = {16, 18, 21}
```

`TOP_LEVEL_HEADING_SIZE` 以上のサイズは `##`、それ未満の候補は `###` になります。
新しいサイズを追加する場合は、両方の値を調整してください。

```python
HEADING_FONT_SIZES = {16, 18, 20, 21}
TOP_LEVEL_HEADING_SIZE = 20
```

見出しではない文字が見出しになる場合は、`HEADING_FONT_SIZES` から該当サイズを外します。

### 箇条書き図形

`・` が文字ではなく小さな塗りつぶし図形として PDF に埋め込まれている場合、次の値で
検出します。

| 定数 | 内容 | 調整方法 |
|---|---|---|
| `PDF_BULLET_MAX_X` | 箇条書き図形の右端の横位置上限 | 箇条書きを拾えない場合は増やす。無関係な図形を拾う場合は減らす |
| `PDF_BULLET_MAX_SIZE` | 箇条書き図形の幅・高さ上限 | 大きい箇条書きを拾う場合は増やす。誤検出時は減らす |
| `PDF_BULLET_Y_TOLERANCE` | 図形と本文の縦位置の許容差 | 対応する本文を拾えない場合は増やす。別行を拾う場合は減らす |

調整例:

```python
PDF_BULLET_MAX_X = 60
PDF_BULLET_MAX_SIZE = 8
PDF_BULLET_Y_TOLERANCE = 4
```

一度にすべてを変更せず、まず `PDF_BULLET_MAX_X`、次に
`PDF_BULLET_Y_TOLERANCE`、最後に `PDF_BULLET_MAX_SIZE` の順で調整すると原因を切り分けやすくなります。

## 注意事項

- 表の複雑な結合セルや特殊なレイアウトは、完全には再現できない場合があります。
- PDF に文字情報がなく画像だけの場合、現在のツール単体では OCR できません。
- PDF のフォントや図形の座標によって、同じ設定でも文書ごとに調整が必要になる場合があります。
- `pdfplumber` がフォントに関する警告を表示しても、変換自体が成功する場合があります。
