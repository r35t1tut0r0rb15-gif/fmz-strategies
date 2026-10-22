# #458146 Multi EMA and Supertrend Crossover Strategy -> `fmz_458146_ema22_79_200_triple_supertrend_state_reversal`

- FMZ source id: 458146 (lineage).
- Source: https://www.fmz.com/strategy/458146 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 12:14:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend with three Supertrend confirmations |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [6.0, 3.0] x `ema_short` [22, 10]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
