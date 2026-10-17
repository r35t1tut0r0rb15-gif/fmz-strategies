# #432221 Dual SuperTrend Strategy -> `fmz_432221_double_band_trend`

- FMZ source id: 432221 (lineage).
- Source: https://www.fmz.com/strategy/432221 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 16:33:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `mult` [3.0, 1.5]: **4 trials**.

## Ambiguities resolved

- The band ratchets as written. Long test first. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
