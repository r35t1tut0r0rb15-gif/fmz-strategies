# #474971 Triple Standard Deviation Bollinger Bands Breakout Strategy with 100 Day Moving Average Optimization -> `fmz_474971_sma100_3sd_breakout_1sd_exit_long`

- FMZ source id: 474971 (lineage).
- Source: https://www.fmz.com/strategy/474971 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-13 11:20:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Asymmetric band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`upper_sd` [3.0, 2.0] x `ma_period` [100, 50]: **4 trials**; lower 1 sd.

## Ambiguities resolved

- Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
