# #477555 RSI与布林带协同波段交易策略-RSI-and-Bollinger-Bands-Synergistic-Swing-Trading-Strategy -> `fmz_477555_bb20_lower_rsi40_dip_profit2_close_long`

- FMZ source id: 477555 (lineage).
- Source: https://www.fmz.com/strategy/477555 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:51:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band / RSI dips with band, RSI and 2 % profit closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; commission / slippage not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `profit_pct` [0.02, 0.04]: **4 trials**; RSI 14 / 60 / 40, 2 sd.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
