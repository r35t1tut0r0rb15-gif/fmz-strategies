# #468335 Adaptive Risk Management Strategy Based on Dual Moving Average Golden Cross -> `fmz_468335_golden_cross_sma200_close_exit_long`

- FMZ source id: 468335 (lineage).
- Source: https://www.fmz.com/strategy/468335 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:17:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Golden crosses with an SMA 200 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-risk quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; the 98.5 % entry guard fixed.

## Ambiguities resolved

- No stop order (the level sizes only). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
