# #432178 三EMA叉加Stochastic-RSI策略3EMA-with-Stochastic-RSI-Strategy -> `fmz_432178_three_ema_stoch_rsi_atr_bracket`

- FMZ source id: 432178 (lineage).
- Source: https://www.fmz.com/strategy/432178 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 10:47:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [3.0, 1.5] x `tp_atr` [2.0, 4.0]: **4 trials**; the EMAs, the stochastic RSI settings and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the fill with the signal bar's ATR; live on the fill bar in the house engine. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
