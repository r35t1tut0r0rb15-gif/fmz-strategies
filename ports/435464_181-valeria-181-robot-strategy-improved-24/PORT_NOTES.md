# #435464 跨趋势跟随套利181策略Valeria-181-Robot-Strategy-Improved-24 -> `fmz_435464_close_sma4_cross_bracket`

- FMZ source id: 435464 (lineage).
- Source: https://www.fmz.com/strategy/435464 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 10:13:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin inputs stored; the price-unit bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435464. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.17, 1.0] x `sma_len` [4, 10]: **4 trials**; the target is 150 / 170 of the stop.

## Ambiguities resolved

- Price-unit bracket -> ATR multiple. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
