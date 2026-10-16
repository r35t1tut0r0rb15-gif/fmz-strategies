# #430853 Hull移动平均的趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy -> `fmz_430853_noro_hullma_one_bar`

- FMZ source id: 430853 (lineage).
- Source: https://www.fmz.com/strategy/430853 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 15:02:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close_all every bar as written. |
| 2 | PASS | The slope of a Hull moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [16, 32, 8]: **3 trials**.

## Ambiguities resolved

- close_all every bar: one-bar holds, as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
