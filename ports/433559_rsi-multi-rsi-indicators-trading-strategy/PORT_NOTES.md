# #433559 多重RSI指标交易策略Multi-RSI-Indicators-Trading-Strategy -> `fmz_433559_noro_rsi_symphony`

- FMZ source id: 433559 (lineage).
- Source: https://www.fmz.com/strategy/433559 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-28 15:03:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot formula and pyramiding 20 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit_shift` [0, -5] x `use_rsi4` [False, True]: **4 trials**; limit_shift moves the three limits (20 / 25 / 30) together; use_rsi4 adds RSI 21 / 35.

## Ambiguities resolved

- Net position ported (pyramiding adds are sizing); colour filter off. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
