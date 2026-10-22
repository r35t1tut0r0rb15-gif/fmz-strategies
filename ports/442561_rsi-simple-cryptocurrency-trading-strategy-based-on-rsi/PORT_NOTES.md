# #442561 基于RSI的简单密码货币交易策略Simple-Cryptocurrency-Trading-Strategy-Based-on-RSI -> `fmz_442561_rsi14_level_reversal_1m`

- FMZ source id: 442561 (lineage).
- Source: https://www.fmz.com/strategy/442561 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 17:44:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [30, 20]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- The closes never fire, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
