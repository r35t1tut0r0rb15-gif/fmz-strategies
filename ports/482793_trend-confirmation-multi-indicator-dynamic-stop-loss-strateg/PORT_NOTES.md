# #482793 Trend Confirmation Multi Indicator Dynamic Stop Loss Strategy -> `fmz_482793_sma30_macd_adx25_state_swing_low_stop_long`

- FMZ source id: 482793 (lineage).
- Source: https://www.fmz.com/strategy/482793 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 11:19:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C249). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing-low stop followed in the loop (pending) |
| 2 | PASS | SMA / MACD / ADX trend state with a swing-low stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [30, 50] x `adx_min` [25, 20]: **4 trials**; MACD 9 / 18 / 9, DMI 14.

## Ambiguities resolved

- The stored swing value is the bar after the swing low, as written. The working stop is pending; the loop closes one bar late.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
