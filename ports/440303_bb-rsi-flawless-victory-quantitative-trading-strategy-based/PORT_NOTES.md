# #440303 双BB指标RSI量化交易策略Flawless-Victory-Quantitative-Trading-Strategy-Based-on-Double-BB-Indicators-and-RSI -> `fmz_440303_flawless_victory_bb_rsi_v1`

- FMZ source id: 440303 (lineage).
- Source: https://www.fmz.com/strategy/440303 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 10:33:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_ll` [42, 30] x `rsi_ul` [70, 76]: **4 trials**; BB 20 / 1.0 and RSI 14 fixed.

## Ambiguities resolved

- Version 1 only. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
