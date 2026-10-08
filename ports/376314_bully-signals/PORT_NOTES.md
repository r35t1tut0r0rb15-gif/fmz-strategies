# #376314 Bully signals -> `fmz_376314_bully_qqe_line_side`

- Source: https://www.fmz.com/strategy/376314 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-08-03 12:01:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_len` [10, 14] x `sf` [5, 6] x `qqe` [3.0, 4.238] = **8 trials**.

## Ambiguities resolved

- Same code as #365028 (ND365028) with RSI 14 / smoothing 6.
- `ta.cross` either direction; Thresh-hold unused.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
