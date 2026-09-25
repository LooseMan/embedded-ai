---
name: company-calender
description: 会社休日に関する依頼を処理するSkill。
---

## MCPツール

祝日の判定には `jholiday` MCPサーバーの以下のToolを使用する。

- 単一日付の判定には `check_holiday` を使用する。
- 複数日付の判定には `check_holidays` を使用する。

## 利用ルール

- 「YYYY年MM月の祝日」の依頼では、対象年・月の全日付をまとめて `check_holidays` で確認する。
- 複数日付を確認する依頼では、可能な限り `check_holidays` を1回呼び出して確認する。
- ツールの結果に含まれる `holiday_name` を回答に使用する。
- MCPツールが利用できない場合は、その旨を明示し、代替手段を使った場合は情報源を示す。
