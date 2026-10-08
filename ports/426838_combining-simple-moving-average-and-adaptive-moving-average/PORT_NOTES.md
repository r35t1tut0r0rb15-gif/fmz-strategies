# #426838 Combining Simple Moving Average and Adaptive Moving Average -> `fmz_426838_iir_alma_cross_long`

- Source: https://www.fmz.com/strategy/426838 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 18:14:34). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426838` (Jaccard >= 0.80) with #439763 (DUPLICATE); best Jaccard 0.931 with #439763. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`iirx` [8, 13] x `iirx2` [89, 144] x `alma_period` [21, 34]: **8 trials**, defaults 13 / 144 / 21 (the source's); periods 21 / 233 and ALMA 0.99 / 8 fixed.

## Ambiguities resolved

- Filter lengths scale with timeframe.multiplier (5): 55 and 6710 bars, as written.
- Fan counts, squeezes, RSI arrows and debug panels do not reach orders.
- Long only. FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
