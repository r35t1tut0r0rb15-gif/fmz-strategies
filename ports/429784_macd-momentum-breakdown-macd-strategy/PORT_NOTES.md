# #429784 动量熔断MACD策略Momentum-Breakdown-MACD-Strategy -> `fmz_429784_momentum_minus_macd_long`

- FMZ source id: 429784 (lineage).
- Source: https://www.fmz.com/strategy/429784 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 17:12:31). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The sign of a difference in the same units. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_len` [10, 20] x `slow` [26, 50]: **4 trials**; EMA 12 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
