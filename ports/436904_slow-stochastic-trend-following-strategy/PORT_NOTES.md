# #436904 Slow Stochastic Trend Following Strategy -> `fmz_436904_slow_stochastic_ob_os`

- FMZ source id: 436904 (lineage).
- Source: https://www.fmz.com/strategy/436904 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 17:50:36). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smooth_k` [400, 200] x `sma_k` [275, 140]: **4 trials**; D 10 and levels 78.5 / 23 fixed.

## Ambiguities resolved

- Call-order fills. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
