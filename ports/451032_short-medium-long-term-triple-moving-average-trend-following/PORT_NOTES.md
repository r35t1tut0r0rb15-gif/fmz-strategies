# #451032 Short Medium Long Term Triple Moving Average Trend Following Strategy -> `fmz_451032_close_under_low_avg3_above_sma30_long`

- FMZ source id: 451032 (lineage).
- Source: https://www.fmz.com/strategy/451032 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 12:04:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dips under the low average in an uptrend, high-average exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [3, 5] x `trend_len` [30, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
