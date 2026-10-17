# #433923 Dual Moving Average Crossover Strategy -> `fmz_433923_sma_10_20_long`

- FMZ source id: 433923 (lineage).
- Source: https://www.fmz.com/strategy/433923 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-01 14:53:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short` [10, 20] x `long` [20, 50]: **4 trials** (10 / 20 as written).

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
