# #434598 基于MACD指标的双向交易策略MACD-based-Dual-Trading-Strategy -> `fmz_434598_macd_hist_turn_exits`

- FMZ source id: 434598 (lineage).
- Source: https://www.fmz.com/strategy/434598 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-07 17:11:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 6] x `slow` [26, 52]: **4 trials**; the SMA 9 signal fixed.

## Ambiguities resolved

- Same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
