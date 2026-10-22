# #440695 基于布林带B指标的长线交易策略Long-Term-Trading-Strategy-Based-on-Bollinger-Bands-B-Indicator -> `fmz_440695_bb_percent_b_dip_long_target`

- FMZ source id: 440695 (lineage).
- Source: https://www.fmz.com/strategy/440695 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 11:15:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry (activation approximated) |
| 2 | PASS | Bollinger %B |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.05, 0.02] x `dev` [2.0, 2.5]: **4 trials**; BB length 20 fixed.

## Ambiguities resolved

- Target held from the fill (the script arms it on a later signal bar). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
