# #428982 Price Volatility Mean Reversion Strategy -> `fmz_428982_noro_vixfix_rsi`

- FMZ source id: 428982 (lineage).
- Source: https://www.fmz.com/strategy/428982 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-11 16:03:36). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Percentages, RSI levels and candle-body ratios. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 5, leverage and the lot formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [40, 30] x `pd` [22, 11]: **4 trials**; BB 20 x 2, percentile 50 x 0.85, RSI 7 and body SMA 10 fixed.

## Ambiguities resolved

- Entry wins over a same-bar close_all. REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`none`
