# #482850 高频价格失衡区域动量交易策略基于指数均线和ATR动态止盈止损-High-Frequency-Fair-Value-Gap-Momentum-Trading-Strategy-with-EMA-and-ATR-Based-Dynamic-Exit -> `fmz_482850_fvg_gap_volume_imbalance_trend_atr_bracket_reversal`

- FMZ source id: 482850 (lineage).
- Source: https://www.fmz.com/strategy/482850 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:18:11). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Three-bar gaps on high volume with a trend filter |
| 3 | PASS | Exchange pair in the header only ("Forex" in the title). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [2.0, 3.0] x `sl_atr` [1.2, 2.0]: **4 trials**; EMA 50 / 200, volume x 1.5, ATR 14.

## Ambiguities resolved

- The "bullish" gap is a gap down, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "gap"`.

## Marks

`coarse_bar_stop`
