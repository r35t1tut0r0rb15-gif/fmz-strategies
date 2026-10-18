# #436252 Noro的快速RSI切换策略v17Fast-Scalping-RSI-Switching-Strategy-v17 -> `fmz_436252_noro_fast_rsi_scalper`

- FMZ source id: 436252 (lineage).
- Source: https://www.fmz.com/strategy/436252 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 15:10:40). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Position-dependent entry conditions followed inside simulate |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital percent and the martingale switch stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426461. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 5] x `limit` [30, 25]: **4 trials**; the other switches at their defaults.

## Ambiguities resolved

- Position-dependent conditions; orders in call order. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
