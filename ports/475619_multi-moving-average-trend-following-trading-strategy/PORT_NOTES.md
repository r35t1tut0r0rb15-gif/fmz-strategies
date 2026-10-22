# #475619 Multi Moving Average Trend Following Trading Strategy -> `fmz_475619_sma50_100_cross_sma200_side_reversal`

- FMZ source id: 475619 (lineage).
- Source: https://www.fmz.com/strategy/475619 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 15:52:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an SMA 200 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `medium` [100, 50]: **4 trials**; slow 200.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
