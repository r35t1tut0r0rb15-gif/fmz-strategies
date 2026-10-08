# #380331 Moving Average Cross -> `fmz_380331_sma_29_69_cross`

- Source: https://www.fmz.com/strategy/380331 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-28 07:42:12). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`fast` [13, 29] x `slow` [44, 69] = **4 trials** (the defaults and the table's BTC row).

## Ambiguities resolved

- Date range 2012-2022 and its close_all are a backtest window: dropped.
- Per-market table only draws.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
