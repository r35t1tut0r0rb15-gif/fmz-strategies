# #428706 Developing a 2 20 Exponential Moving Average Strategy -> `fmz_428706_hpotter_2_20_ema`

- FMZ source id: 428706 (lineage).
- Source: https://www.fmz.com/strategy/428706 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-08 15:14:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Price comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50]: **2 trials**; reverse false fixed.

## Ambiguities resolved

- The first bar has no high[1] (na): no position until both sides are known. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
