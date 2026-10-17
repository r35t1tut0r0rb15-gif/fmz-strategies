# #431919 Moving Average Trading Strategy -> `fmz_431919_negroni_ma_rsi_retest`

- FMZ source id: 431919 (lineage).
- Source: https://www.fmz.com/strategy/431919 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-13 11:17:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (rule 2); adds not ported |
| 2 | PASS | EMAs, RSI levels and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 3 % of equity and pyramiding 3 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 3.0] x `tp_mult` [2.5, 4.0]: **4 trials**; EMAs, RSI levels, ATR 50 and the daily EMA 100 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the ATR bracket re-sized every bar; fixed at the signal bar here. Daily EMA from
  completed broker days. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
