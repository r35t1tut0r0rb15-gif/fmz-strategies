# #452819 波林格带和EMA趋势跟踪策略-Bollinger-Bands-and-EMA-Trend-Following-Strategy -> `fmz_452819_ema9_cross_beyond_bollinger_bracket_reversal`

- FMZ source id: 452819 (lineage).
- Source: https://www.fmz.com/strategy/452819 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 16:49:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-close bracket as fixed fractions; re-issued levels pending (mark) |
| 2 | PASS | EMA crossings beyond the bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [9, 21] x `sl_pct` [0.005, 0.01] x `tp_pct` [0.01, 0.02]: **8 trials**; the bands 20 / 2 fixed.

## Ambiguities resolved

- Re-issued levels pending; opening levels kept. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`trailing_stop_pending`
