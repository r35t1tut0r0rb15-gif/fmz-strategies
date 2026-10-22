# #439101 基于改进型MACD指标的短线交易策略Reverse-Momentum-Trading-Strategy -> `fmz_439101_ergotic_macd_state`

- FMZ source id: 439101 (lineage).
- Source: https://www.fmz.com/strategy/439101 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-17 17:29:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Inverted MACD against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [32, 64] x `fast` [5, 10]: **4 trials**; signal 5 fixed.

## Ambiguities resolved

- Inverted MACD state as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
