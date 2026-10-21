# #438506 Trend Following Strategy with Stop Loss -> `fmz_438506_supertrend_turn_amount_bracket_5m`

- FMZ source id: 438506 (lineage).
- Source: https://www.fmz.com/strategy/438506 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:55:40). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit stop and profit amounts -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [0.0068, 0.02] x `factor` [3.0, 2.0]: **4 trials**; profit_frac 0.018 and ATR 10 fixed.

## Ambiguities resolved

- Price-unit amounts -> fractions of the close; bracket started at the fill. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
