# #430555 Momentum Reversal Combo Strategy -> `fmz_430555_combo_123_dsp`

- FMZ source id: 430555 (lineage).
- Source: https://www.fmz.com/strategy/430555 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 11:49:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit band -> an ATR fraction. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430555, ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_dsp` [14, 28] x `zone_atr` [0.15, 0.5]: **4 trials**; the 123 settings fixed.

## Ambiguities resolved

- Band test order kept; band in price units -> ATR. Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
