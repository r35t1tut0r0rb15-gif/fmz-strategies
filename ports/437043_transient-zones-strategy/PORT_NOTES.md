# #437043 Transient Zones Strategy -> `fmz_437043_noro_transient_zones`

- FMZ source id: 437043 (lineage).
- Source: https://www.fmz.com/strategy/437043 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-29 17:03:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rolling extremes and body ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot and capital % stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`h_left` [10, 20] x `use_body` [True, False]: **4 trials**; colour filter on.

## Ambiguities resolved

- h_right -1 reads the current bar; call-order fills; date window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
