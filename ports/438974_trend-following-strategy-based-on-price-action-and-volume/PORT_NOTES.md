# #438974 Trend Following Strategy Based on Price Action and Volume -> `fmz_438974_sma50_sma25_cross_volume_above_average_1h_reversal`

- FMZ source id: 438974 (lineage).
- Source: https://www.fmz.com/strategy/438974 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 17:34:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ma` [50, 10] x `vol_len` [25, 50]: **4 trials**; long MA 25, 30-bar range.

## Ambiguities resolved

- MA lengths as written (50 over 25). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
