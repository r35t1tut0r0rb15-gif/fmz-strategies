# #437024 Momentum and Money Flow Crossroad Cashing Strategy -> `fmz_437024_stoch20_cross_cmf10_filter_reversal`

- FMZ source id: 437024 (lineage).
- Source: https://www.fmz.com/strategy/437024 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 16:12:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic crossings with a money-flow filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [20, 14] x `cmf_len` [10, 20]: **4 trials**; D 3, levels 0.1 / 0.08 / -0.1 / 0.06.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_cross"`.

## Marks

`none`
