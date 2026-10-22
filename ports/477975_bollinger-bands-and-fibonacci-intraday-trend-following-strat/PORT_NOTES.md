# #477975 Bollinger Bands and Fibonacci Intraday Trend Following Strategy -> `fmz_477975_bb20_extreme_fib_range_reversal`

- FMZ source id: 477975 (lineage).
- Source: https://www.fmz.com/strategy/477975 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 16:29:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | Bollinger extremes inside the Fibonacci range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**; Fibonacci 20 bars, levels 0.236 / 0.618; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar tick bracket kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
