# #473122 Advanced Trend Trading Strategy Based on Bollinger Bands and Candlestick Patterns -> `fmz_473122_daily_bb_wick_rejection_12h_entries_reversal`

- FMZ source id: 473122 (lineage).
- Source: https://www.fmz.com/strategy/473122 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:18:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | Band wick rejections; moving exits described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size (1 % of a 100000 balance) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG473122. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `wick_ratio` [1.0, 2.0]: **4 trials**; the pivot spans fixed; the moving exits pending.

## Ambiguities resolved

- Daily values from the last completed broker day; strict pivots; moving exits pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
