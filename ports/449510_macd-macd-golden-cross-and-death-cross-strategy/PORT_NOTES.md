# #449510 MACD金叉死叉策略-MACD-Golden-Cross-and-Death-Cross-Strategy -> `fmz_449510_macd_signal_cross_rounds_long`

- FMZ source id: 449510 (lineage).
- Source: https://www.fmz.com/strategy/449510 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 12:08:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; the signal length fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
