# #440368 基于平滑RSI的股票交易策略Smoothed-RSI-Based-Stock-Trading-Strategy -> `fmz_440368_smoothed_rsi5_40_80_long`

- FMZ source id: 440368 (lineage).
- Source: https://www.fmz.com/strategy/440368 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 16:26:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 14] x `oversold` [40, 30]: **4 trials**; overbought 80 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
