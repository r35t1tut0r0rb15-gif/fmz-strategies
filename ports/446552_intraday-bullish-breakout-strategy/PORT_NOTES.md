# #446552 Intraday Bullish Breakout Strategy -> `fmz_446552_swing_low_3line_strike_atr_close_tests_long`

- FMZ source id: 446552 (lineage).
- Source: https://www.fmz.com/strategy/446552 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:13:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exits are close tests |
| 2 | PASS | Swing-low / three-line-strike entries with ATR close tests |
| 3 | PASS | No exchange header. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [4.0, 2.0] x `sl_atr` [2.0, 1.0]: **4 trials**; the swing look-back and the ATR length fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); reference price reset by every signal. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`bar_size_pending`
