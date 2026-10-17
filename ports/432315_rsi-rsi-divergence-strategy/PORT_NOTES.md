# #432315 RSI离散分歧策略RSI-Divergence-Strategy -> `fmz_432315_rsi_divergence_long`

- FMZ source id: 432315 (lineage).
- Source: https://www.fmz.com/strategy/432315 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 11:36:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed on past bars |
| 2 | PASS | RSI divergences and levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 2 and pyramiding 2 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND366941. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 9] x `tp_level` [80, 70]: **4 trials**; pivots 1 / 3 and the 5-60 range fixed.

## Ambiguities resolved

- Stop type NONE; adds are sizing. Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`none`
