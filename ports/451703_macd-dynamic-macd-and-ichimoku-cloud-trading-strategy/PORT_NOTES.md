# #451703 动态MACD和一目均衡图交易策略-Dynamic-MACD-and-Ichimoku-Cloud-Trading-Strategy -> `fmz_451703_macd_cross_ichimoku_confirm_tick_bracket_reversal`

- FMZ source id: 451703 (lineage).
- Source: https://www.fmz.com/strategy/451703 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:45:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | MACD crossings with Ichimoku confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.0033, 1.0] x `tp_atr` [0.0067, 2.0]: **4 trials**; the MACD and Ichimoku lengths fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (1h ~150). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
