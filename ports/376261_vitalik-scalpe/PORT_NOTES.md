# #376261 Vitalik Scalpe -> `fmz_376261_pivot_sar_range_filter_rmi_ha_scalp_sets_atr_trend_close_reversal`

- FMZ source id: 376261 (lineage).
- Source: https://www.fmz.com/strategy/376261 (PineScript v4, author a624587332, FMZ last
  modified 2022-08-02 23:55:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill; close-all on the trend flip |
| 2 | PASS | Four-set multi-indicator confluence with an ATR trend exit |
| 3 | PASS | No exchange header. |
| 4 | DONE | 100 % of equity, capital 10000 and commission 0.03 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_f` [1.8, 1.5] x `th` [13.0, 20.0]: **4 trials**; the other settings as written.

## Ambiguities resolved

- The script's CondIni side drives the close-all, as written; a repeat entry on a close-all bar keeps the position (approximation).
- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`bar_size_pending, trailing_stop_pending`
