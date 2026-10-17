# #489153 小时周期价格开口策略追踪开盘与收盘价差的智能对比量化交易系统-Hourly-Open-Close-Price-Differential-Smart-Comparison-Quantitative-Trading-System -> `fmz_489153_gap_up_buy_3pct_target_long`

- FMZ source id: 489153 (lineage).
- Source: https://www.fmz.com/strategy/489153 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:15:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a close-checked target |
| 2 | PASS | A gap test and a percentage |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target_pct` [3.0, 1.0]: **2 trials**; 3 % is the source's.

## Ambiguities resolved

- The 3 % target is close-checked against the fill price (rule 3); no stop exists, as written.
- Entries only from flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action_breakout"`.

## Marks

`none`
