# #437035 博林带RSI交叉策略Bollinger-Bands-and-RSI-Crossover-Strategy -> `fmz_437035_bollinger_rsi_reentry`

- FMZ source id: 437035 (lineage).
- Source: https://www.fmz.com/strategy/437035 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 16:40:19). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `rsi_len` [14, 21]: **4 trials**; 2 sigma and 70 / 30 fixed.

## Ambiguities resolved

- Signals only, reversing. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
