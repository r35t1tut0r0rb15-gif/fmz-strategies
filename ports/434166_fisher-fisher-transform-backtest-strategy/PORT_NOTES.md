# #434166 Fisher变换指标回测策略Fisher-Transform-Backtest-Strategy -> `fmz_434166_fisher_transform_state`

- FMZ source id: 434166 (lineage).
- Source: https://www.fmz.com/strategy/434166 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-04 13:43:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A bounded transform of the range position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434166. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20, 40]: **3 trials**.

## Ambiguities resolved

- Recursions seeded with 0 as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
