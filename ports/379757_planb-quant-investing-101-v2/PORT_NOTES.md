# #379757 PlanB Quant Investing 101 -> `fmz_379757_planb_rsi_bounce`

- Source: https://www.fmz.com/strategy/379757 (PineScript v4, author Zer3192, FMZ last
  modified 2023-12-02 17:49:46). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`sell_level` [80, 90] x `drop` [60, 65] x `buy_level` [40, 50] = **8 trials**.

## Ambiguities resolved

- Same-bar long and short: the later order (short) wins.
- Stop/take-profit option default off.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
