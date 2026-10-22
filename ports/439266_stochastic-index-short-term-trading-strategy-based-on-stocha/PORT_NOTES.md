# #439266 基于Stochastic-Index指标的短线交易策略Short-term-Trading-Strategy-Based-on-Stochastic-Index -> `fmz_439266_smi_45_extremes_state`

- FMZ source id: 439266 (lineage).
- Source: https://www.fmz.com/strategy/439266 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-18 16:14:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sm1` [5, 10] x `level` [45.0, 60.0]: **4 trials**; sm2 3 fixed.

## Ambiguities resolved

- OR chains reduce to the 45 level. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
