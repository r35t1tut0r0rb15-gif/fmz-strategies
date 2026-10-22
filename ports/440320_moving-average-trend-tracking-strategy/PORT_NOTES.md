# #440320 Moving Average Trend Tracking Strategy -> `fmz_440320_chaloke_atr_shifted_ema_lines`

- FMZ source id: 440320 (lineage).
- Source: https://www.fmz.com/strategy/440320 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 11:46:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-shifted EMA lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p1` [9, 5] x `p3` [24, 50]: **4 trials**; the middle period 15 and ATR 5 fixed.

## Ambiguities resolved

- Short wins a same-bar tie. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
