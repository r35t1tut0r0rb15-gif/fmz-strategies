# #444002 基于21日EMA成交量和RSI的趋势动量策略Trend-Momentum-Strategy-Based-on-21-EMA-Volume-and-RSI -> `fmz_444002_ema21_cross_volume_rsi_atr_stop_reversal`

- FMZ source id: 444002 (lineage).
- Source: https://www.fmz.com/strategy/444002 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 14:59:14). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal close as a fraction of the fill |
| 2 | PASS | EMA 21 crossings with volume and RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_pct` [10, 25] x `atr_mult` [1.5, 2.5]: **4 trials**; EMA 21, RSI 14, ATR 14.

## Ambiguities resolved

- Stop fixed at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
