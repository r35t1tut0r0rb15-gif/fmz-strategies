# #438334 Moving Stop Loss Strategy Based on Points Take Profit and Stop Loss -> `fmz_438334_ema_wma_cross_pip_bracket`

- FMZ source id: 438334 (lineage).
- Source: https://www.fmz.com/strategy/438334 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-11 11:04:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Pip bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The pip inputs and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.1, 1.0] x `ema_period` [10, 5]: **4 trials**; WMA 20, ATR 14 and the 1:1 target fixed.

## Ambiguities resolved

- Pip bracket -> ATR multiples (reading and a wider stop). Entries only from flat. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
