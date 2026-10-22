# #473235 Dual Standard Deviation Bollinger Bands Momentum Breakout Strategy -> `fmz_473235_bb34_2sd_close_beyond_band_reversal`

- FMZ source id: 473235 (lineage).
- Source: https://www.fmz.com/strategy/473235 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:10:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts held as states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND455366. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
