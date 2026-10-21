# #438948 Dynamic Trend Tracking Reversal Strategy -> `fmz_438948_jd_aggressive_sequential_7`

- FMZ source id: 438948 (lineage).
- Source: https://www.fmz.com/strategy/438948 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-16 15:35:18). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | High / low counts and support / resistance levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`band` [0.0042, 0.01] x `xx` [True, False]: **4 trials**; the 7 / 5 counts fixed.

## Ambiguities resolved

- Count through same-colour runs; short wins a both-setup bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
