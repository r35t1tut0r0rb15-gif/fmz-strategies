# #430594 VB Strategy Based on Volume Balances -> `fmz_430594_vfi130_band_extreme_flat_entries`

- FMZ source id: 430594 (lineage).
- Source: https://www.fmz.com/strategy/430594 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-30 17:03:02). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume flow indicator band extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1-unit strategy.order adds stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [130, 50] x `signal_length` [5, 10]: **4 trials**; coef 0.2, max 2.5, band 20.

## Ambiguities resolved

- Adds not ported; an opposite signal only closes. Volume = broker tick volume. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
