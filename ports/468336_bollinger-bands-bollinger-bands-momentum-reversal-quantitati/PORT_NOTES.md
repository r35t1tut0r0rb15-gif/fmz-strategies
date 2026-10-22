# #468336 Bollinger-Bands动量反转量化策略Bollinger-Bands-Momentum-Reversal-Quantitative-Strategy -> `fmz_468336_bb34_band_reentry_reversal`

- FMZ source id: 468336 (lineage).
- Source: https://www.fmz.com/strategy/468336 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:21:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries; per-bar band stop described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [34, 20] x `multiplier` [2.0, 2.5]: **4 trials**; the per-bar band stop pending.

## Ambiguities resolved

- Per-bar band stop kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
