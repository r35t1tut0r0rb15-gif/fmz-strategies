# #439080 Momentum Inversion Tracking Strategy -> `fmz_439080_psar_close_cross`

- FMZ source id: 439080 (lineage).
- Source: https://www.fmz.com/strategy/439080 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 15:46:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / SAR crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`increment` [0.02, 0.01] x `maximum` [0.2, 0.1]: **4 trials**; start = increment.

## Ambiguities resolved

- Pine's SAR algorithm. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
