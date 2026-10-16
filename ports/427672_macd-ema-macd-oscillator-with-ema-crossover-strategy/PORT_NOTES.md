# #427672 MACD Oscillator with EMA Crossover Strategy -> `fmz_427672_macd_hist_flip_ema_long`

- FMZ source id: 427672 (lineage).
- Source: https://www.fmz.com/strategy/427672 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-23 15:24:12). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | No exchange in the source. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [9, 21] x `signal_length` [9, 5]: **4 trials**; defaults 9 / 9 (the source's); MACD 12/26 fixed. The bar size is the driver's (`bar_size_pending`), searched per the run spec.

## Ambiguities resolved

- Heikin Ashi off and the short switch off by default: Long only.
- The opened flag follows the signals (as written). time_cond is true.
- No backtest header: `FREQ = "bar_size_pending"` (rule 1) and `precompute` builds the bars from `params["bar_size"]` with the house `bar_sizes.build_bars` (FMZ-C rule C3, skill section 5a).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`bar_size_pending`
