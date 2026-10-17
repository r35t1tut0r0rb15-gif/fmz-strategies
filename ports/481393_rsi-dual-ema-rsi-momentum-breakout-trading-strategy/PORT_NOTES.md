# #481393 双均线RSI动量突破交易策略-Dual-EMA-RSI-Momentum-Breakout-Trading-Strategy -> `fmz_481393_ema50_100_green_rsi70_momentum_long`

- FMZ source id: 481393 (lineage).
- Source: https://www.fmz.com/strategy/481393 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 16:54:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and an RSI level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_ob` [70, 60] x `slow` [100, 200]: **4 trials**; defaults 70 / 100 (the source's); EMA 50 and RSI 14 fixed.

## Ambiguities resolved

- `isGreenConfirmed` equals the green state. The EMA 100 stop is reset on every entry and re-set only after a red bar
  that has already closed the trade: inert, not ported.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
