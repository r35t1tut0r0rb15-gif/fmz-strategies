# #449713 CCIDMI和MACD混合多空策略-CCI-DMI-and-MACD-Hybrid-Long-Short-Strategy -> `fmz_449713_cci_cross_dmi_macd_confirm_reversal`

- FMZ source id: 449713 (lineage).
- Source: https://www.fmz.com/strategy/449713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 13:52:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI crossings with DMI and MACD confirmation, CCI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [14, 20] x `level` [100.0, 150.0]: **4 trials**; the DMI and MACD lengths fixed.

## Ambiguities resolved

- Closes act on held, non-reversed positions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
