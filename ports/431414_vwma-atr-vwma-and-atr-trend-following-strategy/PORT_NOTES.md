# #431414 基于VWMA及ATR的趋势跟踪策略VWMA-and-ATR-Trend-Following-Strategy -> `fmz_431414_vwma33_atr_trailing_state_rsi_long`

- FMZ source id: 431414 (lineage).
- Source: https://www.fmz.com/strategy/431414 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 16:39:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWMA trend entries with an ATR trailing-line exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 10 % / (close x 5 %), 20 % of equity, capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vwma_length` [33, 20] x `atr_mult` [3.5, 2.0]: **4 trials**; ATR 33, RSI 14.

## Ambiguities resolved

- position_size >= 1 read as in a position. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
