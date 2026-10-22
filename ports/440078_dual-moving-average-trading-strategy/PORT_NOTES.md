# #440078 Dual Moving Average Trading Strategy -> `fmz_440078_double_ema_alignment_session`

- FMZ source id: 440078 (lineage).
- Source: https://www.fmz.com/strategy/440078 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-26 14:45:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Double-EMA alignment and a UTC session |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length0` [5, 8] x `length1` [21, 34]: **4 trials**; session fixed.

## Ambiguities resolved

- Session on the UTC bar open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
