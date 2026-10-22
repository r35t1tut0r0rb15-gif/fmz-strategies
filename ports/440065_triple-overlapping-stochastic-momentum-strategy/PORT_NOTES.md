# #440065 Triple Overlapping Stochastic Momentum Strategy -> `fmz_440065_triple_smi_below_signal_state`

- FMZ source id: 440065 (lineage).
- Source: https://www.fmz.com/strategy/440065 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-26 12:15:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMI against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`nsig` [10, 5] x `q2` [20, 40]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- Contrarian reading as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
