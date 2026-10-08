# #380277 Gooners BTC Weekly RSI Hack Strategy -> `fmz_380277_rsi_52_long_only`

- Source: https://www.fmz.com/strategy/380277 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-27 21:19:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() / order sizing lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 14, 21] x `level` [50, 52, 55] (one level for both, as the defaults) = **9 trials**.

## Ambiguities resolved

- Long only, as written (rule 6).
- Title says weekly; the header runs 4 h bars, used as the source's setting.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
