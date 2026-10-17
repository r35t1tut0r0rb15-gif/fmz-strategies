# #431426 基于交易量平均价和Stairstep-EMA-的策略Volume-Price-Trend-Reversal-Forex-Trading-Strategy-Based-on-Stairstep-EMA -> `fmz_431426_fractal_ema_stack_fade`

- FMZ source id: 431426 (lineage).
- Source: https://www.fmz.com/strategy/431426 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-07 17:03:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick target / stop -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [2, 3] x `bracket_atr` [0.17, 1.0]: **4 trials**; equal target and stop (as the source's equal 25 / 25); EMAs 10 / 20 / 100 fixed.

## Ambiguities resolved

- Swapped entries as written; tick bracket as ATR fractions (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
