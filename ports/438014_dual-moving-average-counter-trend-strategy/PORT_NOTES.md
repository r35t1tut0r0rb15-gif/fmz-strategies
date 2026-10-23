# #438014 Dual Moving Average Counter Trend Strategy -> `fmz_438014_ema28_vs_daily_ema28_cross_inverted_2h_reversal`

- FMZ source id: 438014 (lineage).
- Source: https://www.fmz.com/strategy/438014 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 11:01:11). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Chart EMA against the daily EMA (inverted) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [28, 50] x `inverse` [1, 0]: **4 trials**; session 09-23 UTC.

## Ambiguities resolved

- Inverted signals, as written; daily EMA of the last completed day. Volume not used. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
