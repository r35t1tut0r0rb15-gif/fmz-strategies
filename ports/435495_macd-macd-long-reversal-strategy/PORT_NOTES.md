# #435495 MACD长线反转策略MACD-Long-Reversal-Strategy -> `fmz_435495_macd_histogram_turn_long`

- FMZ source id: 435495 (lineage).
- Source: https://www.fmz.com/strategy/435495 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 13:55:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum histogram turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [6, 12] x `slow` [26, 21]: **4 trials**; the signal SMA 9 fixed.

## Ambiguities resolved

- Two rising bars; exit on a fall under two bars back. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
