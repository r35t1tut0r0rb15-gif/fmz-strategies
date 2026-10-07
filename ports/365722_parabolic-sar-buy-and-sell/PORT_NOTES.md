# #365722 Parabolic SAR (PSAR Buy and Sell Alerts) -> `fmz_365722_psar_side_flip`

- Source: https://www.fmz.com/strategy/365722 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-25 18:23:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

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

`start` [0.00252, 0.02] x `increment` [0.00133, 0.02] x `maximum` [0.2, 0.22] = **8 trials** (the originals and the classic 0.02 / 0.02 / 0.2).

## Ambiguities resolved

- sar() as documented by TradingView (pine_sar).
- dir = psar < close ? 1 : -1 (na SAR counts as -1, as coded).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
