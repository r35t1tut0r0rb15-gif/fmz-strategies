# #432913 Moving Average Crossover Strategy -> `fmz_432913_ema_26_51_atr_bracket`

- FMZ source id: 432913 (lineage).
- Source: https://www.fmz.com/strategy/432913 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-22 16:38:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | FX tick-scaled ATR distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 3.0] x `tp_atr` [1.0, 2.0]: **4 trials**; EMA 26 / 51 and ATR 14 fixed.

## Ambiguities resolved

- FX tick factor read as ATR multiples. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
