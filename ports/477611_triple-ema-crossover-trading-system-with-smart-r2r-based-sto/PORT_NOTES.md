# #477611 Triple EMA Crossover Trading System with Smart R2R based Stop Loss Management -> `fmz_477611_ema8_21_cross_ema89_side_tight_bracket_reversal`

- FMZ source id: 477611 (lineage).
- Source: https://www.fmz.com/strategy/477611 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:53:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill; break-even described (pending) |
| 2 | PASS | EMA crossings on the EMA 89 side with a tight bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop / target fractions stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.001, 0.005] x `tp_pct` [0.0025, 0.01]: **4 trials**; EMA 8 / 21 / 89; the break-even pending.

## Ambiguities resolved

- Break-even stop not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
