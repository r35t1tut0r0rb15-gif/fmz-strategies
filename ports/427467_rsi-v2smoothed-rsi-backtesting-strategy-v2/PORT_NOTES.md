# #427467 Smoothed RSI Backtesting Strategy V2 -> `fmz_427467_hpotter_smoothed_rsi_v2`

- FMZ source id: 427467 (lineage).
- Source: https://www.fmz.com/strategy/427467 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 15:02:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.
- Near-duplicate group: **DG427467** (with #427880, Jaccard 0.800); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Ratio of price moves. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427467. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20, 5] x `top_band` [0.8, 0.7]: **6 trials**; defaults 10 / 0.8 (the source's); the low band is 1 - top (0.2 by default, as the source's).

## Ambiguities resolved

- A high ratio buys (as written). REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
