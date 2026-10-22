# #458242 HMA优化多周期量化交易策略与动态止损结合-Optimized-Multi-Timeframe-HMA-Quantitative-Trading-Strategy-with-Dynamic-Stop-Loss -> `fmz_458242_hull55_turn_one_tick_trail_long`

- FMZ source id: 458242 (lineage).
- Source: https://www.fmz.com/strategy/458242 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:28:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | Hull average turns with a tight trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 180] x `trail_pct` [0.0000024, 0.01]: **4 trials**; the Hull mode Hma fixed.

## Ambiguities resolved

- Session always true on daily bars; WMA length 27 for 55 / 2; the tick trail as a percent of 42000. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`coarse_bar_stop, trailing_stop`
