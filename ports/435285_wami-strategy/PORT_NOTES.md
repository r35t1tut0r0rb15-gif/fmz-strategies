# #435285 WAMI Strategy -> `fmz_435285_wami_sign`

- FMZ source id: 435285 (lineage).
- Source: https://www.fmz.com/strategy/435285 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-13 17:42:01). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length_ema` [13, 8]: **4 trials**; WMA 4 and trigger 0 fixed.

## Ambiguities resolved

- State changes only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
