# #440977 Bollinger Bands Breakout Quantitative Trading Strategy -> `fmz_440977_bollinger_breakout_band_return_exit`

- FMZ source id: 440977 (lineage).
- Source: https://www.fmz.com/strategy/440977 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 14:52:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 20] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
