# #436783 基于SMA均线和RSI指标的白银价格短期交易策略Short-Term-Silver-Trading-Strategy-Based-on-SMA-and-RSI-Indicators -> `fmz_436783_sma_cross_rsi_atr_bracket`

- FMZ source id: 436783 (lineage).
- Source: https://www.fmz.com/strategy/436783 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 16:42:05). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ATR bracket around the signal bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG436783, ND430053. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [30, 60]: **4 trials**; RSI 14, ATR 14 and the 3 / 2 ATR brackets fixed.

## Ambiguities resolved

- Bracket from the signal bar's levels as distances; re-arming of an open bracket not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
