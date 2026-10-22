# #442349 Momentum Indicator Aggregation Trading Strategy -> `fmz_442349_any_of_momentum_signals_reversal`

- FMZ source id: 442349 (lineage).
- Source: https://www.fmz.com/strategy/442349 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 11:59:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Any-of momentum signals |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `ema_long` [100, 200]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- Date bound dropped (EMA terms always on); the long is checked first. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
