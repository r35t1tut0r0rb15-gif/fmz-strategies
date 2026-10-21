# #437399 多重RSI指标聚合策略Strategy-of-Synthesis-between-Multiple-Relative-Strength-Indicators -> `fmz_437399_noro_rsi_symphony_long`

- FMZ source id: 437399 (lineage).
- Source: https://www.fmz.com/strategy/437399 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-02 12:06:14). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 20 and the equity-based lot stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period1` [4, 3] x `rsi_limit1` [15.0, 10.0]: **4 trials**; the other four RSIs fixed.

## Ambiguities resolved

- Pyramiding adds left out (sizing); shorts never ordered. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
