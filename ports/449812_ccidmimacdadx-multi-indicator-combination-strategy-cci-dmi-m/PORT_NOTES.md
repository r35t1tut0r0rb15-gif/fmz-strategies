# #449812 CCIDMIMACDADX Multi Indicator Combination Strategy CCI DMI MACD ADX -> `fmz_449812_cci_cross_dmi_adx_macd_confirm_reversal`

- FMZ source id: 449812 (lineage).
- Source: https://www.fmz.com/strategy/449812 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 14:06:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI crossings with DMI, ADX and MACD confirmation, CCI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [14, 20] x `adx_min` [20.0, 25.0]: **4 trials**; the levels, the DMI and MACD lengths fixed.

## Ambiguities resolved

- Closes act on held, non-reversed positions. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
