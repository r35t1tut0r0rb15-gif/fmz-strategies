# #441078 Bollinger Bands Dual track Breakthrough Strategy -> `fmz_441078_bb_touch_basis_stop_reversal`

- FMZ source id: 441078 (lineage).
- Source: https://www.fmz.com/strategy/441078 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 14:05:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger touches and the basis test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `stop_pct` [1.0, 2.0]: **4 trials**; stdev 2 fixed.

## Ambiguities resolved

- Closes in call order on the held position. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
