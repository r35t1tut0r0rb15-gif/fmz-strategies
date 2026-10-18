# #436008 基于RSI-SMA的突发性买卖策略SMA-RSI-Sudden-Buy-Sell-Strategy -> `fmz_436008_rsi_sma_sudden_reversals`

- FMZ source id: 436008 (lineage).
- Source: https://www.fmz.com/strategy/436008 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 17:33:04). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crossings, RSI levels and a jump rule |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `bars` [10, 5]: **4 trials**; the other lengths and levels fixed.

## Ambiguities resolved

- Counters and flags as written; orders in call order. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
