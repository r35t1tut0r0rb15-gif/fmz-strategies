# #433901 快速RSI反转策略Fast-RSI-Reversal-Strategy -> `fmz_433901_noro_fast_rsi_fade`

- FMZ source id: 433901 (lineage).
- Source: https://www.fmz.com/strategy/433901 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 13:37:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and body ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and pyramiding 5 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG433901. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [25, 15] x `rsi_len` [3, 5]: **4 trials**; body EMA 30 / 2 fixed.

## Ambiguities resolved

- Net position ported (pyramiding adds are sizing); entry wins over a same-bar exit. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
