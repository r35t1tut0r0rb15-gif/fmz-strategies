# #432845 Quant Trading Double Click Reversal Strategy -> `fmz_432845_reversal123_klinger_volume_oscillator_combo_reversal`

- FMZ source id: 432845 (lineage).
- Source: https://www.fmz.com/strategy/432845 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 10:03:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and volume-oscillator states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_x` [34, 20] x `slow_x` [55, 89]: **4 trials**; 123 reversal 14 / 1 / 3 / 50, trigger 13.

## Ambiguities resolved

- Volume = broker tick volume (Klinger). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`
