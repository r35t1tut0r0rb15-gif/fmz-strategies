# #483045 多均线趋势交叉三重过滤交易策略-Triple-Moving-Average-Cross-Filter-Trading-System -> `fmz_483045_sma21_50_cross_sma100_filter_long`

- FMZ source id: 483045 (lineage).
- Source: https://www.fmz.com/strategy/483045 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 10:48:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 10] x `trend` [100, 200]: **4 trials**; defaults 21 / 100 (the source's); SMA 50 fixed.

## Ambiguities resolved

- Long only: opposite entries cannot occur. No stops. "Gold" in the title is a label. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
