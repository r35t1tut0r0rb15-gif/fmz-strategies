# #491892 EMA双重交叉动态止损量化策略-EMA-Dual-Crossover-Dynamic-Stop-Loss-Quantitative-Strategy -> `fmz_491892_ema_10_20_cross_ema50_trend`

- FMZ source id: 491892 (lineage).
- Source: https://www.fmz.com/strategy/491892 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 16:59:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `trend` [50, 100]: **4 trials**; defaults 10 / 50 (the source's); slow EMA 20 fixed.

## Ambiguities resolved

- The EMA 10 closes act on the position held at the bar's start (written after the entries).
- isBullish / isBearish keep the side of the last cross, as written (they gate the closes).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
