# #452276 Dynamic Trend Momentum Trading Strategy -> `fmz_452276_macd_cross_ema50_rsi_vwap_half_tick_trail_4h_reversal`

- FMZ source id: 452276 (lineage).
- Source: https://www.fmz.com/strategy/452276 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-23 17:57:22). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail from the fill |
| 2 | PASS | MACD crossings with EMA, RSI and VWAP filters |
| 3 | PASS | Exchange pair in the header only; the tick offset converted at the source's BTC price. |
| 4 | DONE | Entry qty 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [7.6e-07, 0.01] x `ema_len` [50, 100]: **4 trials**; MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- Half-tick trail converted at the source's BTC price, activated at the fill. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`coarse_bar_stop, trailing_stop, trailing_stop_pending`
