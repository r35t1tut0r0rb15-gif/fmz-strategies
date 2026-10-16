# #430269 双重Stochastic底部反转策略Combined-Stochastic-Oscillator-and-123-Reversal-Strategy -> `fmz_430269_combo_123_stochastic`

- FMZ source id: 430269 (lineage).
- Source: https://www.fmz.com/strategy/430269 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 17:00:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_s` [7, 14] x `up_band` [20, 50]: **4 trials**; down band 80 and the 123 settings fixed.

## Ambiguities resolved

- Band order kept as written. Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
