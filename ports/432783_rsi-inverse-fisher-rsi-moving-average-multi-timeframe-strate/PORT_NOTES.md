# #432783 逆向费希尔RSI平均真实范围多时间框架策略Inverse-Fisher-RSI-Moving-Average-Multi-Timeframe-Strategy -> `fmz_432783_inverse_fisher_rsi_as_written`

- FMZ source id: 432783 (lineage).
- Source: https://www.fmz.com/strategy/432783 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 14:45:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A transformed RSI against fixed levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [5, 9] x `scale` [10.0, 0.1]: **4 trials**; the 0.8 level fixed (10 as written; 0.1 gives an unsaturated transform).

## Ambiguities resolved

- The short cross under a boolean, as written (intent owed). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
