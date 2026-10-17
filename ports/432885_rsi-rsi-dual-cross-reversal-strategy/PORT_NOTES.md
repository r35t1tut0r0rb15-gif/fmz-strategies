# #432885 RSI双叉反转策略RSI-Dual-Cross-Reversal-Strategy -> `fmz_432885_rsi_5_11_cross_after_extreme`

- FMZ source id: 432885 (lineage).
- Source: https://www.fmz.com/strategy/432885 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 14:59:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crosses and levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `slow` [11, 21]: **4 trials**; RSI 6 and the 30 / 70 levels fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
