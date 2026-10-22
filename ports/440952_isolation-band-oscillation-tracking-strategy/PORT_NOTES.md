# #440952 Isolation Band Oscillation Tracking Strategy -> `fmz_440952_chandelier_flip_ratio_exits`

- FMZ source id: 440952 (lineage).
- Source: https://www.fmz.com/strategy/440952 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 10:28:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-tested stop, target and trail |
| 2 | PASS | Chandelier stops |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash size, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [22, 14] x `mult` [3.0, 2.0]: **4 trials**; the ratio exits fixed.

## Ambiguities resolved

- Ratio exits bar-tested against the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
