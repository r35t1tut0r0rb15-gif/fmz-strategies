# #362887 FTL - Range Filter X2 + EMA + UO -> `fmz_362887_range_filter_uo_ema`

- Source: https://www.fmz.com/strategy/362887 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-13 16:11:48). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`per2` [30, 48] x `mult2` [2.6, 3.4] x `ema_len` [100, 144] = **8 trials**. UO 7/14/28 and levels 60/40 stay at the originals.

## Ambiguities resolved

- The conditions compare the leading source (hl2) with the trigger filter (ohlc4), as coded; the leading filter, EMA crosses and pullback markers only draw.
- `src > src[1] or src < src[1]` -> `src != src[1]`.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
