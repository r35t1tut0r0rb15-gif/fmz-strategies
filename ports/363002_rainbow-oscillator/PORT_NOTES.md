# #363002 Rainbow Oscillator -> `fmz_363002_rainbow_oscillator_level_return`

- Source: https://www.fmz.com/strategy/363002 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 23:11:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 24, 34] x `level_period` [12, 18] = **6 trials**. Weights, stochastic 40, SMA 4 and redundancy 0.99 stay at the originals.

## Ambiguities resolved

- `ta.rma` re-seeds with an SMA when its previous value is na (Pine definition), so early na levels recover.
- "% Take profit" / "% Stop Loss" are declared but never used; not ported.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
