# #440957 Triple Exponential Moving Average Profit Taking and Stop Loss Strategy -> `fmz_440957_ema21_55_cross_atr_bracket_long`

- FMZ source id: 440957 (lineage).
- Source: https://www.fmz.com/strategy/440957 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 10:38:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA crossings and ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [3, 2] x `sl_mult` [2, 1]: **4 trials**; EMA 55 / 21 / 9 and ATR 14 fixed.

## Ambiguities resolved

- Bracket from the signal close. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
