# #474683 Multi EMA Trend Following Trading Strategy -> `fmz_474683_ema10_30_50_trend_recross_ema30_reversal`

- FMZ source id: 474683 (lineage).
- Source: https://www.fmz.com/strategy/474683 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:44:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend re-crossings of the middle EMA with EMA-cross exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `mid_len` [30, 20] x `long_len` [50, 100]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
