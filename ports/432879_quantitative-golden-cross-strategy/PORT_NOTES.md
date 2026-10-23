# #432879 Quantitative Golden Cross Strategy -> `fmz_432879_signed_volume_cross_avg_volume_1m_reversal`

- FMZ source id: 432879 (lineage).
- Source: https://www.fmz.com/strategy/432879 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-22 14:39:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Signed-volume crossings of its average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mav_len` [3, 10, 20]: **3 trials**.

## Ambiguities resolved

- Exits without prices send nothing, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
