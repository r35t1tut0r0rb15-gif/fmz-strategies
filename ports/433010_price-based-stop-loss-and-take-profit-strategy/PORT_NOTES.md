# #433010 Price based Stop Loss and Take Profit Strategy -> `fmz_433010_sma_cross_money_bracket`

- FMZ source id: 433010 (lineage).
- Source: https://www.fmz.com/strategy/433010 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 15:36:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Money (price-unit) distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The money-to-points conversion by position size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG433010. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [3.3, 1.5] x `sl_atr` [1.7, 1.0]: **4 trials**; SMA 14 / 28 and ATR 14 fixed.

## Ambiguities resolved

- Dollar distances per contract as ATR fractions (criterion 2 ADAPT), re-based on the fill. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
