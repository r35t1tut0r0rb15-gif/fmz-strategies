# #429476 Adaptive Volatility Finite Volume Elements Strategy -> `fmz_429476_volatility_fve22_ema40_state_reversal`

- FMZ source id: 429476 (lineage).
- Source: https://www.fmz.com/strategy/429476 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-17 14:50:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Finite volume elements against its EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`samples` [22, 50] x `perma` [40, 20]: **4 trials**; cutoffs 0.1 / 0.1.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_index"`.

## Marks

`none`
