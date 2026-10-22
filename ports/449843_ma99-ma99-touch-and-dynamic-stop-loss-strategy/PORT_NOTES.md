# #449843 MA99接触与动态止损策略-MA99-Touch-and-Dynamic-Stop-Loss-Strategy -> `fmz_449843_sma99_touch_two_close_stop_reversal`

- FMZ source id: 449843 (lineage).
- Source: https://www.fmz.com/strategy/449843 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 16:59:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop is a two-close test |
| 2 | PASS | SMA touches with a two-close stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [99, 50]: **2 trials**.

## Ambiguities resolved

- Two-close stop at the saved SMA level. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
