# #472971 Dual Moving Average Crossover Trend Following Strategy with Dynamic Stop Loss and Take Profit System -> `fmz_472971_ema50_sma200_cross_reversal`

- FMZ source id: 472971 (lineage).
- Source: https://www.fmz.com/strategy/472971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 17:24:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- The exits are comments (no stop or target). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
