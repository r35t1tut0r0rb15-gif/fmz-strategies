# #440309 Cross Cycle Arbitrage Strategy Based on Multiple Indicators -> `fmz_440309_quarrylake_keltner_vstop_wae`

- FMZ source id: 440309 (lineage).
- Source: https://www.fmz.com/strategy/440309 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 11:10:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner line, volatility stop and MACD-change explosion |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (a Kelly note in a comment only). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [5, 2] x `sensitivity` [150, 300]: **4 trials**; the lengths fixed.

## Ambiguities resolved

- Volatility-stop warm-up approximate. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
