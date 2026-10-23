# #438379 Support and Resistance Strategy with Volume Breakout and Trailing Stop Loss -> `fmz_438379_pivot_sr_break_volume_osc_atr_line_30m_flat_only`

- FMZ source id: 438379 (lineage).
- Source: https://www.fmz.com/strategy/438379 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-11 17:58:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR line exits in the signals |
| 2 | PASS | Pivot support / resistance breaks on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (risk 200 input feeds a commented line). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.2, 2.0] x `vol_break` [20, 10]: **4 trials**; pivots 10 / 15, EMA 150.

## Ambiguities resolved

- ATR line followed in the signals; session in UTC; the close_all never fires on 30-minute bars. Volume = broker tick volume. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`trailing_stop_pending`
