# #484583 Bollinger Precision Risk Optimization Strategy -> `fmz_484583_bb20_2_reentry_rsi14_4_8pct_bracket_reversal`

- FMZ source id: 484583 (lineage).
- Source: https://www.fmz.com/strategy/484583 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:07:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Bollinger re-entries with RSI extremes |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 2 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percent` [4.0, 2.0] x `take_profit_percent` [8.0, 4.0]: **4 trials**; Bollinger 20 / 2, RSI 14 / 30 / 70.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
