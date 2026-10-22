# #451526 Bollinger-Bands-Dynamic-Breakout-Strategy-动态布林带突破策略 -> `fmz_451526_bollinger34_breakout_band_reentry_exit_reversal`

- FMZ source id: 451526 (lineage).
- Source: https://www.fmz.com/strategy/451526 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 16:25:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts with a re-entry exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger"`.

## Marks

`none`
