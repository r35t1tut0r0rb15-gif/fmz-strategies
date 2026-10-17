# #434332 Momentum Index ETF Trend Following Strategy -> `fmz_434332_sma_50_150_slope_long`

- FMZ source id: 434332 (lineage).
- Source: https://www.fmz.com/strategy/434332 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 15:13:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses and an ATR-normalised slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-percent unit count and the initial capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 25] x `slope_deg` [5, 10]: **4 trials**; SMA 150, ATR 14 fixed; the exit angle is minus the entry angle.

## Ambiguities resolved

- Flat-only entries, long-only exits (state machine). The slope exit threshold mirrors the entry one in the grid. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
