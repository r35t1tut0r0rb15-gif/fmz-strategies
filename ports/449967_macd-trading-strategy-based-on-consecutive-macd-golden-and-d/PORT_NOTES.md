# #449967 基于连续MACD金叉死叉的交易策略-Trading-Strategy-Based-on-Consecutive-MACD-Golden-and-Death-Crosses -> `fmz_449967_macd_cross_one_pct_bracket_reversal`

- FMZ source id: 449967 (lineage).
- Source: https://www.fmz.com/strategy/449967 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 17:26:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | MACD signal crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.01, 0.02] x `sl` [0.01, 0.005]: **4 trials**; the MACD lengths fixed (one value each for the two sides, as their defaults agree).

## Ambiguities resolved

- Every crossing trades (flag set before the test). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
