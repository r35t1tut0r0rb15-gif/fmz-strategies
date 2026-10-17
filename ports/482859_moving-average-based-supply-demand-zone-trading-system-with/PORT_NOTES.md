# #482859 基于移动平均线和供需区域的动态风险管理交易系统-Moving-Average-Based-Supply-Demand-Zone-Trading-System-with-Dynamic-Risk-Management -> `fmz_482859_sma_cross_near_zone_pct_bracket`

- FMZ source id: 482859 (lineage).
- Source: https://www.fmz.com/strategy/482859 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:39:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (decision owed). |
| 2 | PASS | Moving averages, remembered swing levels and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_lookback` [50, 100] x `tp_pct` [2.0, 3.0]: **4 trials**; defaults 50 / 2 (the source's); SMA 9 / 21, strength 2
and the 1 % stop fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on signal bars from `strategy.position_avg_price` (na while flat). The port applies the
1 % / 2 % bracket from the fill (the evident intent), as #489289.

## Ambiguities resolved

- The zones are `var` levels kept until replaced (na before the first). REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
