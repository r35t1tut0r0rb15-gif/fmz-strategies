# #442812 基于超趋势和CCI策略的短线交易Supertrend-and-CCI-Scalping-Strategy -> `fmz_442812_raw_stoch_rsi_level_reversal`

- FMZ source id: 442812 (lineage).
- Source: https://www.fmz.com/strategy/442812 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 10:44:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_length` [14, 7] x `oversold` [10, 20]: **4 trials** (overbought = 100 - oversold); the RSI length fixed.

## Ambiguities resolved

- Raw stochastic (smoothing unused). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
