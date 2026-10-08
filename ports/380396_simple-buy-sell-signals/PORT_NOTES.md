# #380396 Simple Buy Sell Signals -> `fmz_380396_ma_cross_rsi_side`

- Source: https://www.fmz.com/strategy/380396 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-28 18:30:25). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

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

`rsi_len` [9, 14] x `ma2_len` [21, 35] = **4 trials**.

## Ambiguities resolved

- Both signals use the upward crossover (short is not a crossunder): kept as written.
- DMI computed but unused.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
