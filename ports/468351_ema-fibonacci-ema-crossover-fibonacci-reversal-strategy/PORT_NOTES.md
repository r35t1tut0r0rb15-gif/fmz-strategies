# #468351 EMA交叉Fibonacci反转策略-EMA-Crossover-Fibonacci-Reversal-Strategy -> `fmz_468351_ema50_side_zone_rsi_low_entries_reversal`

- FMZ source id: 468351 (lineage).
- Source: https://www.fmz.com/strategy/468351 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 17:33:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA, retracement-zone and RSI-low entries; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `lookback` [20, 50]: **4 trials**; the RSI and zone levels fixed; the per-bar bracket pending.

## Ambiguities resolved

- Never-true parts kept as written; per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
