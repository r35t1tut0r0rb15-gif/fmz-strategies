# #432077 ANN based Quantitative Trading Strategy -> `fmz_432077_fixed_ann_daily_change`

- FMZ source id: 432077 (lineage).
- Source: https://www.fmz.com/strategy/432077 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-14 11:22:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A fixed function of a percentage change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders (the network is fixed): **1 trial**, the source as written.

## Ambiguities resolved

- Previous broker day's ohlc4; weights as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
