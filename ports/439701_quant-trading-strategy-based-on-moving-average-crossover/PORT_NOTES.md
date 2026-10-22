# #439701 Quant Trading Strategy Based on Moving Average Crossover -> `fmz_439701_ema3_5_cross_tick_bracket_long`

- FMZ source id: 439701 (lineage).
- Source: https://www.fmz.com/strategy/439701 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-23 11:05:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.00125, 0.5]: **2 trials**; target / stop 6 / 5 and EMA 3 / 5 fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples. Long only. FREQ = "5h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
