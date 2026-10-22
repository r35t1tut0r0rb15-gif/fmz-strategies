# #482917 基于Nadaraya-Watson的多维度整合交易策略-Multi-Dimensional-Integration-Trading-Strategy-Based-on-Nadaraya-Watson -> `fmz_482917_nw_composite_sma10_cross_sma200_rsi50_pct_bracket_reversal`

- FMZ source id: 482917 (lineage).
- Source: https://www.fmz.com/strategy/482917 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:21:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Smoothed composite crossing its SMA with trend / RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smooth_length` [20, 10] x `take_profit_perc` [3.0, 2.0]: **4 trials**; bandwidth 20, weights 0.4 / 0.2 / 0.2 / 0.2, SMA 200, RSI 50, stop 1.5 %.

## Ambiguities resolved

- The kernel's heaviest weight is on the oldest bar, as written. The bracket is ported from the fill, active from the fill bar.
- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
