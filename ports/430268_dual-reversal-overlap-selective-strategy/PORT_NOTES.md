# #430268 Dual Reversal Overlap Selective Strategy -> `fmz_430268_combo_123_dss_bressert`

- FMZ source id: 430268 (lineage).
- Source: https://www.fmz.com/strategy/430268 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 16:56:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pds` [10, 20] x `ema_len` [9, 5]: **4 trials**; trigger 5, 80 / 20 and the 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
