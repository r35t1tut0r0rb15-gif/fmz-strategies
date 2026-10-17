# #432234 Trend Following Energy Indicator Trading Strategy -> `fmz_432234_smeared_vci_cross`

- FMZ source id: 432234 (lineage).
- Source: https://www.fmz.com/strategy/432234 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-15 17:36:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick distances -> ATR multiples / a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the slippage stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smear` [34, 17] x `sl_atr` [0.15, 1.0]: **4 trials**; EMA 5 / 13, ATR 96, trigger 13 and the trail fixed.

## Ambiguities resolved

- Tick exits as ATR multiples / fractions (stated). REVERSAL INTENDED. Mark trailing_stop. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop`
