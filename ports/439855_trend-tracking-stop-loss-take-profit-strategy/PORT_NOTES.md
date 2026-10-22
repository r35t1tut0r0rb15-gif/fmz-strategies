# #439855 Trend Tracking Stop Loss Take Profit Strategy -> `fmz_439855_follow_line_flip_one_bar_long`

- FMZ source id: 439855 (lineage).
- Source: https://www.fmz.com/strategy/439855 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 14:17:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the wrong-side stop read as a close signal |
| 2 | PASS | Bollinger signal and an ATR trend line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND368736. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [21, 50] x `atr_period` [5, 14]: **4 trials**; BB deviation 1 and the 10 % short target fixed.

## Ambiguities resolved

- Longs last one bar (wrong-side stop); shorts have a 10 % target. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
