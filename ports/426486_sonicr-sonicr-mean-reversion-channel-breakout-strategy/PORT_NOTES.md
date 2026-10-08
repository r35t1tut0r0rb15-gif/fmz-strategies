# #426486 SonicR Mean Reversion Channel Breakout Strategy -> `fmz_426486_sonicr_ema_cross`

- Source: https://www.fmz.com/strategy/426486 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 15:09:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

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

`hilo_len` [21, 34] x `ema_signal` [89, 144]: **4 trials**, defaults 34 / 89 (the source's).

## Ambiguities resolved

- The high / low PAC EMAs only plot; orders read EMA 34 of the close against EMA 89.
- FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
