# #439877 Dual Moving Average Crossover Trading Strategy -> `fmz_439877_ema21_55_cross_atr_bracket`

- FMZ source id: 439877 (lineage).
- Source: https://www.fmz.com/strategy/439877 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-24 15:24:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA crossings and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 3.0] x `tp_mult` [1.0, 2.0]: **4 trials**; EMA 21 / 55 and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the signal bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
