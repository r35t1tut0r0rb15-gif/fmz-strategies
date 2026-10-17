# #433960 双均线与RSI组合的MT5马丁格尔scalping策略RSI-and-Moving-Average-Combination-MT5-Martingale-Scalping-Strategy -> `fmz_433960_stoch_rsi_extreme_hold`

- FMZ source id: 433960 (lineage).
- Source: https://www.fmz.com/strategy/433960 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 17:56:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The martingale lot formula stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`osc_len` [5, 14] x `rsi_band` [30, 40]: **4 trials**; zones 80 / 50 fixed; the short RSI level is 100 - rsi_band.

## Ambiguities resolved

- Martingale lot unused (sizing). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
