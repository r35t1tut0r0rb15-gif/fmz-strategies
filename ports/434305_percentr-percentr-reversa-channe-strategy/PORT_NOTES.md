# #434305 反转PercentR连费通道策略PercentR-Reversa-Channe-Strategy -> `fmz_434305_percent_r_band_one_bar`

- FMZ source id: 434305 (lineage).
- Source: https://www.fmz.com/strategy/434305 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 12:04:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An oscillator band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The unused order-size line stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 7] x `low_marker` [-87, -95]: **4 trials**; the high marker -20 fixed.

## Ambiguities resolved

- One-bar trades as written (the session-end exit owed). Unused daily values dropped. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "williams_r_oscillator"`.

## Marks

`none`
