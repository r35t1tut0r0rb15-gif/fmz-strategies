# #440684 Dynamic Moving Average Crossover Strategy -> `fmz_440684_sma9_21_cross_resent_bracket`

- FMZ source id: 440684 (lineage).
- Source: https://www.fmz.com/strategy/440684 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 10:42:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [9, 5] x `slow_length` [21, 50]: **4 trials**.

## Ambiguities resolved

- Re-sent bracket pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
