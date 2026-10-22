# #482904 基于多重级别EMA与RSI动态势能强度的比特币跨周期趋势交易策略-Multi-Timeframe-Bitcoin-Trading-Strategy-Based-on-EMA-and-RSI-Dynamic-Momentum-Strength -> `fmz_482904_weekly_ema20_regime_atr5_low7_ratchet_close_long`

- FMZ source id: 482904 (lineage).
- Source: https://www.fmz.com/strategy/482904 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:24:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based ratchet exit |
| 2 | PASS | Weekly EMA regime with an ATR ratchet |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 10] x `regime_atr` [0.25, 0.5]: **4 trials**; ATR 5, ratchet 7 bars, RSI filter off.

## Ambiguities resolved

- The weekly value is the last completed broker week before the bar's week (security without lookahead, then [1]).
- RSI filter off by default, not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
