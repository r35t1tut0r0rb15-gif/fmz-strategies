# #481393 双均线RSI动量突破交易策略-Dual-EMA-RSI-Momentum-Breakout-Trading-Strategy -> `fmz_481393_ema50_100_green_band_rsi70_long`

- FMZ source id: 481393 (lineage).
- Source: https://www.fmz.com/strategy/481393 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 16:54:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA band trend with an RSI breakout entry |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_small` [50, 20] x `rsi_level` [70, 60]: **4 trials**; EMA 100, RSI 14.

## Ambiguities resolved

- The stop exit never acts, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
