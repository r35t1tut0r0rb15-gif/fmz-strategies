# #473140 Adaptive Bollinger Breakout with Moving Average Quantitative Strategy System -> `fmz_473140_bb20_band_breakout_reversal`

- FMZ source id: 473140 (lineage).
- Source: https://www.fmz.com/strategy/473140 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 15:55:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-based quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `std_dev` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
