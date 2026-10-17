# #435160 Schaff Trend Cycle with Double Moving Average Crossover Strategy -> `fmz_435160_stc_ema_trend_bracket`

- FMZ source id: 435160 (lineage).
- Source: https://www.fmz.com/strategy/435160 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 17:43:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital-based order size stored; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cycle` [10, 20] x `k_atr` [0.11, 1.0]: **4 trials**; MACD 23 / 50, %D 3 / 3 and EMA 35 / 200 fixed.

## Ambiguities resolved

- Tick bracket -> ATR multiple. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
