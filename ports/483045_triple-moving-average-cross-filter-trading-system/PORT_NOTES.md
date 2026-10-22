# #483045 Triple Moving Average Cross Filter Trading System -> `fmz_483045_sma21_50_cross_sma100_filter_long`

- FMZ source id: 483045 (lineage).
- Source: https://www.fmz.com/strategy/483045 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 10:48:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [21, 10] x `trend_filter_length` [100, 200]: **4 trials**; slow SMA 50.

## Ambiguities resolved

- MPL 2.0 source, ported and stated. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
