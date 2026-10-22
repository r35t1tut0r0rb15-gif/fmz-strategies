# #442624 Trend Following Strategy Based on Moving Average Crossover -> `fmz_442624_noro_sma15_30_trend_state_reversal`

- FMZ source id: 442624 (lineage).
- Source: https://www.fmz.com/strategy/442624 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-23 12:21:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA trend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [15, 9] x `slow` [30, 50]: **4 trials**.

## Ambiguities resolved

- SMA defaults; colour filter off. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
