# #435268 基于MACD的复合量化交易策略Compound-Quantitative-Trading-Strategy-Based-on-MACD -> `fmz_435268_macd_cross_long`

- FMZ source id: 435268 (lineage).
- Source: https://www.fmz.com/strategy/435268 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 16:44:46). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal SMA 9 fixed.

## Ambiguities resolved

- Date window unused. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
