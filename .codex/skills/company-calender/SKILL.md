---
name: company-calender
description: 会社休日に関する依頼を処理するSkill。
---

## MCPツール

祝日の判定には `jholiday` MCPサーバーの `check_holiday` ツールを使用する。

## 利用ルール

- 「YYYY年MM月の祝日」の依頼では、対象年・月の各日を `check_holiday` で確認する。
- ツールの結果に含まれる `holiday_name` を回答に使用する。
- MCPツールが利用できない場合は、その旨を明示し、代替手段を使った場合は情報源を示す。
