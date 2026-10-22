# #473372 Momentum Indicator Oscillation Threshold Enhanced Trading Strategy -> `fmz_473372_cci12_below_m90_up_close_exit_long`

- FMZ source id: 473372 (lineage).
- Source: https://www.fmz.com/strategy/473372 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:40:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI dips with an up-close exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 20] x `threshold` [-90, -150]: **4 trials**; stop and target off.

## Ambiguities resolved

- Stop / target off (default). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
