# #436597 Relative Strength Index Stop Loss Strategy -> `fmz_436597_rsi7_extremes_percent_stop`

- FMZ source id: 436597 (lineage).
- Source: https://www.fmz.com/strategy/436597 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-26 10:22:44). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Tick stop on a signal bar -> percent stop on every trade |
| 3 | PASS | No exchange header at all. |
| 4 | DONE | The stop input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `stop_pct` [0.01, 0.02]: **4 trials**; limits 37 / 75 fixed. The bar size is the driver's (`bar_size_pending`), searched per the run spec.

## Ambiguities resolved

- No backtest header: bar_size_pending. Tick stop on a signal bar read as a percent stop. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`bar_size_pending`
