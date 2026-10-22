# #473271 Adaptive Range Volatility Trend Following Trading Strategy -> `fmz_473271_asctrend_wpr_state_flip_reversal`

- FMZ source id: 473271 (lineage).
- Source: https://www.fmz.com/strategy/473271 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:24:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Williams %R state flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`asc_length` [10, 20] x `risk` [3, 6]: **4 trials**; eternal off.

## Ambiguities resolved

- eternal off (default). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
