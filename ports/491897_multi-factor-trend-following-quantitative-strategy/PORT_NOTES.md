# #491897 多因子趋势追踪量化策略-Multi-Factor-Trend-Following-Quantitative-Strategy -> `fmz_491897_sar_ema_rsi_adx_bracket`

- FMZ source id: 491897 (lineage).
- Source: https://www.fmz.com/strategy/491897 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 17:23:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | SAR, oscillators and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 2 %-risk quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [30, 20] x `atr_mult` [1.5, 2.5]: **4 trials**; defaults 30 / 1.5 (the source's); SAR 0.02 / 0.02 /
0.2, EMA 2, RSI 6 (60 / 40), DMI 14 / 14 and the 2:1 reward ratio fixed.

## Ambiguities resolved

- The bracket is placed on the signal bar from its close and ATR; re-based on the fill (house rule).
- ta.sar as documented by TradingView (as #428699); DMI with fixnan (as #426579).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D"; stops on daily bars: `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`coarse_bar_stop`
