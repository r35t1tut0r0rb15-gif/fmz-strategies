# #437031 Quantitative Dual indicator Strategy -> `fmz_437031_ema_2_20_bull_power_combo`

- FMZ source id: 437031 (lineage).
- Source: https://www.fmz.com/strategy/437031 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 16:29:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | EMA side test; the bull-power level is a price unit that cannot bind |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429466. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `bp_len` [15, 30]: **4 trials**; level -15 fixed; reverse off.

## Ambiguities resolved

- Bull-power test always true after its warm-up (shorts only in the warm-up), as written; start window dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
