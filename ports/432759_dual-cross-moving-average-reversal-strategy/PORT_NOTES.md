# #432759 Dual Cross Moving Average Reversal Strategy -> `fmz_432759_combo_123_bear_power`

- FMZ source id: 432759 (lineage).
- Source: https://www.fmz.com/strategy/432759 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-21 11:28:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The price-unit bear-power levels -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430543. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sell_atr` [0.3, 1.0] x `buy_atr` [0.03, 0.3]: **4 trials**; the 123 settings and ATR 14 fixed.

## Ambiguities resolved

- Price-unit levels as ATR fractions (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
