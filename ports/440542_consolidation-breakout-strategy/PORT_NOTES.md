# #440542 Consolidation Breakout Strategy -> `fmz_440542_bollinger_band_breakout_reversal`

- FMZ source id: 440542 (lineage).
- Source: https://www.fmz.com/strategy/440542 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 15:08:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

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

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Closes name missing ids. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
