# #482421 Trend Breakout Trading Strategy Based on Dual Moving Averages and Volume -> `fmz_482421_sma9_21_cross_rising_volume_first_entry_stop_2h_long_only`

- FMZ source id: 482421 (lineage).
- Source: https://www.fmz.com/strategy/482421 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 13:38:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; low-checked stop from the first entry price, in the signals |
| 2 | PASS | SMA crossings on rising high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.05] x `fast` [9, 12]: **4 trials**; SMA 21, volume SMA 20 x 1.5.

## Ambiguities resolved

- Stop level stuck at the first trade's entry. Volume = broker tick volume. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
