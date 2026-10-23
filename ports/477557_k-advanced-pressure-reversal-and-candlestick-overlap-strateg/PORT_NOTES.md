# #477557 高级压力反转与K线重叠策略Advanced-Pressure-Reversal-and-Candlestick-Overlap-Strategy -> `fmz_477557_pressure_reversal_candle_overlap_20pct_target_3h_reversal`

- FMZ source id: 477557 (lineage).
- Source: https://www.fmz.com/strategy/477557 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:54:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 20 % target at the signal close as a fraction of the fill |
| 2 | PASS | Contrarian volume-pressure and body-overlap candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 0.1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.2, 0.05] x `vol_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- Target at the first signal's close; repeats re-send it (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
