# #365691 Profit Maximizer -> `fmz_365691_pmax_ema_cross`

- Source: https://www.fmz.com/strategy/365691 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-25 17:13:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365691` (Jaccard >= 0.80) with #426590 (DUPLICATE); best Jaccard 0.855 with #426590. Group `ND365691` (Jaccard 0.65-0.80) with #438816 (PORT_CANDIDATE), #439094 (PORT_CANDIDATE); best Jaccard 0.711 with #438816. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 14] x `mult` [2.0, 3.0] x `ma_len` [10, 20] = **8 trials**.

## Ambiguities resolved

- MA type default EMA of hl2; "Normalize ATR" default false.
- Stops ratchet against the MA, not the close, as coded.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`
