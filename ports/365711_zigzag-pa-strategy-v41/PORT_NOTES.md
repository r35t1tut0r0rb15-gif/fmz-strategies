# #365711 [STRATEGY][RS]ZigZag PA Strategy V4.1 -> `fmz_365711_zigzag_harmonic_patterns`

- Source: https://www.fmz.com/strategy/365711 (PineScript v2/v3 (+ some v5 calls), author ChaoZhang, FMZ last
  modified 2022-05-25 18:08:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing / trade-size inputs -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND365711` (Jaccard 0.65-0.80) with #439751 (PORT_CANDIDATE); best Jaccard 0.688 with #439751. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ew_rate` [0.236, 0.382] x `tp_rate` [0.618, 1.0] x `sl_rate` [-0.236, -0.382] = **8 trials**.

## Ambiguities resolved

- Alt timeframe "60" equals the 1 h chart: no higher-timeframe read.
- strategy.close checks the bar's high/low at the close and fills next open: exit signal, not a stop; not applied on its own entry bar; same-side entries ignored (pyramiding 0).
- Pattern ratios that divide by zero are na and fail their tests.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
