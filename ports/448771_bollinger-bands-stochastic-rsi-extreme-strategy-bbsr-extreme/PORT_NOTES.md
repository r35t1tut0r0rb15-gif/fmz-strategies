# #448771 Bollinger Bands Stochastic RSI Extreme Strategy BBSR Extreme Strategy -> `fmz_448771_band_reentry_stochrsi_extreme_reversal`

- FMZ source id: 448771 (lineage).
- Source: https://www.fmz.com/strategy/448771 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-18 16:55:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed stop not ported (mark) |
| 2 | PASS | Band re-entries after stochastic-RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the 1.5 % stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `upper_limit` [90.0, 80.0]: **4 trials**; the lower limit and the stochastic-RSI lengths fixed.

## Ambiguities resolved

- Late-armed stop pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
