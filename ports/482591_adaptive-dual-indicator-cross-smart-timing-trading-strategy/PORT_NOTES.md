# #482591 自适应双重指标交叉智能择时交易策略-Adaptive-Dual-Indicator-Cross-Smart-Timing-Trading-Strategy -> `fmz_482591_rsi_cci_extreme_dwell_rsi_cci_exit`

- FMZ source id: 482591 (lineage).
- Source: https://www.fmz.com/strategy/482591 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 10:56:59). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI and CCI levels and changes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stay` [2, 1] x `cci_level` [120, 100]: **4 trials**; defaults 2 / 120 (the source's on the 60-minute chart); RSI 30,
RSI 14 (31 / 69) and CCI 20 fixed.

## Ambiguities resolved

- The timeframe tables resolve on the 60-minute chart to RSI 30, CCI 20, 2 bars; the "stayed below -100" signals
  feed no order.
- Long: `bar_index - t0 >= 2`; short: `<= 2` (true from the first bar in the zone), as written.
- The open flags follow the position; no close on the entry's own bar. Exits only on going flat. REVERSAL INTENDED.
- CCI uses the mean absolute deviation. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
