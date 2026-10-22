# #440437 双指数移动平均线RSI交易策略Double-Exponential-Moving-Average-RSI-Trading-Strategy -> `fmz_440437_dema_rsi_cross_session_trail`

- FMZ source id: 440437 (lineage).
- Source: https://www.fmz.com/strategy/440437 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-30 15:44:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick trail and bracket -> house trail and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Size 1 and capital are sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_k` [0.1, 1.0] x `ma_length` [21, 10]: **4 trials**; RSI 4 / 4, activation 0.00036 and the session fixed.

## Ambiguities resolved

- Tick trail as a house trail (approximation); session on the UTC bar open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop`
