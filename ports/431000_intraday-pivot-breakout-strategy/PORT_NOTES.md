# #431000 Intraday Pivot Breakout Strategy -> `fmz_431000_pivot_breakout_ema_filter`

- FMZ source id: 431000 (lineage).
- Source: https://www.fmz.com/strategy/431000 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-03 16:35:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (rule 2) |
| 2 | PASS | Pivots, an EMA and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 60-unit order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rightbars` [15, 5] x `atr_mult` [3.2, 2.0]: **4 trials**; leftbars 10 and EMA 150 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-issued at the latest close -+ 3.2 ATR; fixed at the signal bar here.
- Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
