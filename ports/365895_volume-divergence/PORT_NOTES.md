# #365895 Volume Divergence -> `fmz_365895_signed_volume_wma_stack_regular_divergence_reversal`

- FMZ source id: 365895 (lineage).
- Source: https://www.fmz.com/strategy/365895 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-26 17:04:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price / signed-volume divergences at pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vl1` [5, 8] x `lb` [5, 3]: **4 trials**; the later stages follow the source's sums (vl2 8), range 5-60.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
