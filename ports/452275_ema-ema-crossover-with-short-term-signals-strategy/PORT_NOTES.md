# #452275 EMA均线交叉与短期信号策略-EMA-Crossover-with-Short-term-Signals-Strategy -> `fmz_452275_ema30_high_low_channel_long`

- FMZ source id: 452275 (lineage).
- Source: https://www.fmz.com/strategy/452275 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-23 17:52:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA high / low channel states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 20, 50]: **3 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
