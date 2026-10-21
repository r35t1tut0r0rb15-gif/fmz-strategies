# #438054 Supertrend Moving Stop Loss Take Profit Strategy -> `fmz_438054_supertrend_turn_price_bracket`

- FMZ source id: 438054 (lineage).
- Source: https://www.fmz.com/strategy/438054 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 16:24:03). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

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

`stop_frac` [0.036, 0.05] x `factor` [3.0, 2.0]: **4 trials**; profit_frac 0.36, ATR 10 and the 0.91 / 1.01 closes fixed.

## Ambiguities resolved

- Price-unit amounts -> fractions of the close; bracket started at the fill. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
