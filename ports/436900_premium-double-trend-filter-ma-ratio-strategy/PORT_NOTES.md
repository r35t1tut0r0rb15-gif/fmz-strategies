# #436900 Premium Double Trend Filter MA Ratio Strategy -> `fmz_436900_ma_ratio_percentile_bracket`

- FMZ source id: 436900 (lineage).
- Source: https://www.fmz.com/strategy/436900 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 17:37:14). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; brackets fixed at entry |
| 2 | ADAPT | Tick brackets -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_length` [50, 100] x `k_atr` [0.25, 1.0]: **4 trials**; fast 10, thresholds 10 / 90, BB 20 / 2 / 30, trend SMA 50 / 200 fixed.

## Ambiguities resolved

- Nearest exit per side (long 50 / 50, short 100 / 150 ticks) -> ATR multiples; time filter off. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
