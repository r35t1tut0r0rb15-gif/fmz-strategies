# #444344 基于UT-Bot指标的ATR移动止损策略UT-Bot-Indicator-Based-ATR-Trailing-Stop-Strategy -> `fmz_444344_close_above_sma50_long_entries`

- FMZ source id: 444344 (lineage).
- Source: https://www.fmz.com/strategy/444344 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-11 11:17:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop not ported (mark) |
| 2 | PASS | Close above the SMA 50 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the 20 % trailing stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG444344. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [50, 100]: **2 trials**.

## Ambiguities resolved

- Ratcheting stop not ported (trailing_stop_pending); no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
