# #439594 Trend Following Strategy Based on Historical High -> `fmz_439594_running_high_drawdown_buy_long`

- FMZ source id: 439594 (lineage).
- Source: https://www.fmz.com/strategy/439594 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 08:59:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractions of the running high |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_frac` [0.8, 0.9] x `sell_frac` [0.99, 0.95]: **4 trials**.

## Ambiguities resolved

- Running high from the data start, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
