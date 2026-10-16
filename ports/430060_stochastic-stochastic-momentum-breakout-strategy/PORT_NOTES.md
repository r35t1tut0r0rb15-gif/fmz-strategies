# #430060 Stochastic动量突破策略Stochastic-Momentum-Breakout-Strategy -> `fmz_430060_stochastic_pop_drop`

- FMZ source id: 430060 (lineage).
- Source: https://www.fmz.com/strategy/430060 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-24 16:35:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Stochastic levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out cash order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`osc_len` [14, 7] x `band` [5, 10]: **4 trials**; lines 50 +- band (55 / 45 default), SMA 2 fixed.

## Ambiguities resolved

- Commented-out strategy() line: orders read as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
