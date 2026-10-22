# #442006 Byron Serpent Cloud Quant Strategy -> `fmz_442006_ichimoku_stochrsi_weighted_vote_reversal`

- FMZ source id: 442006 (lineage).
- Source: https://www.fmz.com/strategy/442006 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-18 15:36:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku and stochastic-RSI vote |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`decision_weight` [50, 40] x `base_periods` [26, 52]: **4 trials**; the other weights and lengths fixed.

## Ambiguities resolved

- Vote as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
