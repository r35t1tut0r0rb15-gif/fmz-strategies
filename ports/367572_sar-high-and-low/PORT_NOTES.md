# #367572 SAR -high and low -> `fmz_367572_sar_envelope_cross`

- Source: https://www.fmz.com/strategy/367572 (PineScript v4, author Zer3192, FMZ last
  modified 2022-06-04 08:50:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

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

`look_back` [20, 40] x `multi` [1.0, 2.0] = **4 trials**. SAR 0.02/0.02/0.2 stays at the original.

## Ambiguities resolved

- sar() as documented by TradingView (pine_sar); population stdev.
- Envelope is of the SAR series itself.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
