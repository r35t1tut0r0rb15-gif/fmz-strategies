# #439188 Dual Factor Momentum Tracking Reversal Strategy -> `fmz_439188_reversal123_laguerre_rsi_combo`

- FMZ source id: 439188 (lineage).
- Source: https://www.fmz.com/strategy/439188 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 11:33:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close patterns, stochastic and a Laguerre RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `gamma` [0.5, 0.7]: **4 trials**; K smoothing 1, D 3, level 50 and bands 0.8 / 0.2 fixed.

## Ambiguities resolved

- Laguerre seeds 1 as written; disagreement closes. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
