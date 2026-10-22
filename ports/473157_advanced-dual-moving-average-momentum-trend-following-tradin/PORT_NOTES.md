# #473157 Advanced Dual Moving Average Momentum Trend Following Trading System -> `fmz_473157_sma11_31_trend_sma5_filter_long`

- FMZ source id: 473157 (lineage).
- Source: https://www.fmz.com/strategy/473157 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:54:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA trend with a short filter |
| 3 | PASS | Exchange pair in the header only (Nifty named in the title). |
| 4 | DONE | Fixed quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [11, 5] x `slow` [31, 50] x `filt` [5, 10]: **8 trials**.

## Ambiguities resolved

- Date window dropped; header's 3-hour bars followed. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
